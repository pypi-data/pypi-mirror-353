//
// SPDX-FileCopyrightText: Copyright 2024-2025 Arm Limited and/or its affiliates <open-source-office@arm.com>
//
// SPDX-License-Identifier: Apache-2.0
//
// Licensed under the Apache License, Version 2.0 (the License); you may
// not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an AS IS BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//

#include "scheduler_decompose.hpp"

#include "common/logging.hpp"

#include "shape_util.hpp"

#include <numeric>
#include <optional>

namespace regor
{

static constexpr int MAX_DIM = 65536;

Flags<QueryResult> OperatorQuery(Architecture *arch, const SchedulerOperation *schedOp, ArchRequirements *req)
{
    ArchOperatorQuery query{};
    const SchedulerConnection *ofmConn = schedOp->OFM();
    Set(query.ifm[0], schedOp->IFM(0));
    Set(query.ifm[1], schedOp->TryIFM(1));
    Set(query.ofm, ofmConn);
    query.transposeMask = ofmConn->transpose;
    query.reverseMask = ofmConn->reverse;
    query.kernel = schedOp->Kernel();
    if ( schedOp->HasAttribute<axis_attr_t>() )
    {
        query.axis = schedOp->Attribute<axis_attr_t>()->axis;
        if ( query.axis >= 0 )
        {
            // Convert axis to negative notation
            query.axis -= query.ifm[0].shape.Size();
        }
    }
    return arch->Constraints()->OperatorQuery(schedOp->Type(), &query, req);
}

bool ShouldDecompose(Architecture *arch, const SchedulerOperation *schedOp)
{
    return CanDecompose(arch, schedOp) && NeedsDecompose(arch, schedOp);
}

static std::unique_ptr<SchedulerOperation> MakeMemCopy(const std::shared_ptr<SchedulerTensor> &source,
    const std::shared_ptr<SchedulerTensor> &dest, const TensorSlice *ofmSlice = nullptr)
{
    assert(ofmSlice == nullptr || ofmSlice->shape + ofmSlice->offset <= dest->storageShape);
    auto op = std::make_unique<SchedulerOperation>(OpType::MemoryCopy);

    op->SetKernel(Kernel::UnitKernel());

    auto ofmConn = op->ConnectOutput(TensorUsage::OFM, dest);
    ofmConn->shape = Shape::PadAxes(dest->storageShape, 4, 1);
    if ( ofmSlice ) ofmConn->slice = *ofmSlice;
    if ( ofmConn->Type() == DataType::Int64 )
    {  // Copy int64 data as int32 data with 2 x C
        ofmConn->SetType(DataType::Int32);
        ofmConn->shape = ofmConn->shape.WithDepth(2 * ofmConn->shape.Depth());
        if ( ofmSlice )
        {
            ofmConn->slice.offset = ofmSlice->offset.WithDepth(2 * ofmSlice->offset.Depth());
            ofmConn->slice.shape = ofmSlice->shape.WithDepth(2 * ofmSlice->shape.Depth());
        }
    }

    auto ifmConn = op->ConnectInput(TensorUsage::IFM, source);
    if ( ifmConn->Type() == DataType::Int64 )
    {  // Copy int64 data as int32 data with 2 x C
        ifmConn->SetType(DataType::Int32);
        ifmConn->shape = source->storageShape.WithDepth(2 * source->storageShape.Depth());
    }
    assert(ifmConn->Type() == ofmConn->Type());
    ifmConn->shape = ofmConn->SliceShape();

    return op;
}

static std::unique_ptr<SchedulerOperation> MakeTransposeOp(
    const std::shared_ptr<SchedulerTensor> &source, const std::shared_ptr<SchedulerTensor> &dest, const Shape &perm)
{
    assert(source->dataType == dest->dataType);
    assert(source->storageShape.Size() == perm.Size());
    auto op = std::make_unique<SchedulerOperation>(OpType::Transpose);

    op->SetKernel(Kernel::UnitKernel());

    const auto attr = op->Attribute<transpose_attr_t>();
    attr->perm = perm;

    auto ifmConn = op->ConnectInput(TensorUsage::IFM, source);
    ifmConn->shape = ifmConn->tensor->storageShape;
    if ( ifmConn->Type() == DataType::Int64 )
    {  // Read int64 data as int32 data with dimensions [..., C, 2]
        ifmConn->SetType(DataType::Int32);
        ifmConn->shape = ifmConn->shape.Insert(ifmConn->shape.Size(), 2);
        attr->perm = perm.Insert(perm.Size(), perm.Size());  // Update permutation with added dimension
    }

    auto ofmConn = op->ConnectOutput(TensorUsage::OFM, dest);
    ofmConn->transpose = TransposeTypeFromShape(attr->perm);
    if ( ofmConn->Type() == DataType::Int64 )
    {  // Write int64 data as int32, with dimensions from ifm
        ofmConn->SetType(DataType::Int32);
    }
    ofmConn->shape = ifmConn->shape.Permute(uint32_t(ofmConn->transpose));
    ofmConn->tensor->producers.push_back(op.get());

    return op;
}

static std::unique_ptr<SchedulerOperation>
MakeSubOperation(const SchedulerOperation *schedOp, const Kernel *newKernel = nullptr, OpType type = OpType::None)
{
    assert(schedOp->SubOps().empty());
    assert(schedOp->Parent() == nullptr);
    auto subOp = std::make_unique<SchedulerOperation>(type != OpType::None ? type : schedOp->Type());
    subOp->SetKernel(newKernel ? *newKernel : *schedOp->Kernel());
    subOp->SetHasScaling(schedOp->HasScaling());
    subOp->_srcKey = schedOp->_srcKey;
    subOp->SetPrimaryIfmIndex(schedOp->PrimaryIfmIndex());
    subOp->SetAttributes(schedOp->AttributeRef());
    subOp->SetAccumulatorMode(schedOp->AccumulatorMode());
    for ( const auto *list : {&schedOp->inputs, &schedOp->outputs} )
    {
        for ( const auto &item : list->pairs() )
        {
            auto usage = item.first;
            const auto &connection = item.second;
            if ( IsOFM(usage) )
            {
                connection.tensor->producers.push_back(subOp.get());
                *subOp->AddOutput(usage) = connection;
            }
            else
            {
                connection.tensor->consumers.push_back(subOp.get());
                *subOp->AddInput(usage) = connection;
            }
        }
    }
    return subOp;
}

static auto GetArchAccumulatorSource(const AccumulatorControl &ac)
{
    switch ( ac.source )
    {
        case AccumulatorSource::Reset:
            return ArchAccumulatorSource::Reset;
        case AccumulatorSource::Acc:
            return ArchAccumulatorSource::Acc;
        case AccumulatorSource::Ifm2:
            return ArchAccumulatorSource::Ifm2;
        default:
            assert(false);
            return ArchAccumulatorSource::Reset;
    }
}

static std::unique_ptr<ArchitectureOpConfig> GetOpConfig(Architecture *arch, const SchedulerOperation *schedOp)
{
    auto *ifm = schedOp->IFM(0);
    auto *ifm1 = schedOp->TryIFM(1);
    auto *ofm = schedOp->OFM();
    regor::ArchitectureConfigQuery qConfig;
    qConfig.ofmShape = Shape::PadAxes(ofm->SliceShape(), 3, 1);
    qConfig.ifmShape[0] = ifm->SliceShape();
    if ( ifm1 )
    {
        qConfig.ifmShape[1] = ifm1->SliceShape();
    }
    qConfig.ifmBits = DataTypeSizeBits(ifm->Type());
    qConfig.ofmBits = DataTypeSizeBits(ofm->Type());
    qConfig.kernel = schedOp->Kernel();
    qConfig.lutBytes = schedOp->TryInput(TensorUsage::LUT) ? 2048 : 0;
    qConfig.scaled = schedOp->HasScaling();
    qConfig.ifmResampling = ifm->resamplingMode;
    qConfig.ofmShape = qConfig.ofmShape.Unpermute(uint32_t(ofm->transpose));
    qConfig.transpose = ofm->transpose;
    qConfig.ofmFormat = ofm->tensor->format;
    const auto &accMode = schedOp->AccumulatorMode();
    qConfig.accSource = GetArchAccumulatorSource(accMode);
    qConfig.accOutputEnabled = accMode.outputEnabled;
    return arch->GetOpConfig(schedOp->Type(), qConfig);
}

bool NeedsDecompose(Architecture *arch, const SchedulerOperation *schedOp)
{
    ArchRequirements req{};
    Flags<QueryResult> result = OperatorQuery(arch, schedOp, &req);
    // Assert complete query
    if ( result.Any(QueryResult::Unsupported) )
    {
        // Operations completely unsupported by HW should not be decomposed
        return false;
    }
    if ( result.Any(QueryResult::HasRequirements) )
    {
        if ( req.req.Any(ArchRequirement::Decompose) )
        {
            return true;
        }
        // Has requirements but not decomposition-related
    }
    // no opconfig requires decomposition
    return !GetOpConfig(arch, schedOp);
}

bool CanDecompose(Architecture *, const SchedulerOperation *schedOp)
{
    if ( schedOp->Type() == OpType::Conv2D ) return true;
    if ( schedOp->Type() == OpType::Conv3D ) return true;
    if ( schedOp->Type() == OpType::DepthwiseConv2D ) return true;
    if ( schedOp->Type() == OpType::TransposeConv2D ) return true;
    if ( DecomposeAsElementwise(schedOp->Type()) || schedOp->Type() == OpType::MemoryCopy ) return true;
    if ( schedOp->Type() == OpType::MatMul ) return true;
    if ( schedOp->Type() == OpType::Resize ) return true;
    if ( schedOp->Type() == OpType::ReduceSum ) return true;
    if ( schedOp->Type() == OpType::ReduceMin ) return true;
    if ( schedOp->Type() == OpType::ReduceMax ) return true;
    if ( schedOp->Type() == OpType::ReduceAny ) return true;
    if ( schedOp->Type() == OpType::ReduceAll ) return true;
    if ( schedOp->Type() == OpType::ArgMax ) return true;
    if ( schedOp->Type() == OpType::Reverse ) return true;
    if ( schedOp->Type() == OpType::Transpose ) return true;
    if ( schedOp->Type() == OpType::AvgPool ) return true;
    if ( schedOp->Type() == OpType::MaxPool ) return true;
    if ( schedOp->Type() == OpType::Resize ) return true;
    return false;
}

typedef std::function<std::vector<std::unique_ptr<SchedulerOperation>>(Architecture *, std::unique_ptr<SchedulerOperation>)> DecomposeFunc;

static std::vector<std::unique_ptr<SchedulerOperation>> DecomposeBlocksElementwise(
    Architecture *arch, std::unique_ptr<SchedulerOperation> op, Shape &blockShape, const DecomposeFunc &doDecompose)
{
    std::vector<std::unique_ptr<SchedulerOperation>> result;
    const auto BH = blockShape.Height();
    const auto BW = blockShape.Width();
    const auto BC = blockShape.Depth();
    auto *ofmConn = op->OFM();
    auto *ifmConn = op->IFM(0);
    auto *ifm2Conn = op->TryIFM(1);
    auto &ofmShape = ofmConn->SliceShape();
    const auto N = Shape::DivRoundUp(ofmShape, blockShape);  // Block count per dimension
    auto NewIfmSlice = [&](SchedulerConnection *ifmC, int x, int y, int c)
    {
        auto newIfmSlice = ifmC->slice;

        newIfmSlice.offset += Shape(y * BH, x * BW, c * BC);
        auto &newIfmShape = newIfmSlice.shape;
        newIfmSlice.shape = Shape::Max(
            Shape::Min(newIfmShape - Shape(y * BH, x * BW, c * BC), Shape(BH, BW, BC)), newIfmShape.WithOnes());
        return newIfmSlice;
    };
    for ( auto by = 0; by < N.Height(); by++ )
    {
        for ( auto bx = 0; bx < N.Width(); bx++ )
        {
            for ( auto bc = 0; bc < N.Depth(); bc++ )
            {
                auto newIfmSlice = NewIfmSlice(ifmConn, bx, by, bc);
                TensorSlice newIfm2Slice;
                if ( ifm2Conn )
                {
                    newIfm2Slice = NewIfmSlice(ifm2Conn, bx, by, bc);
                }
                auto newOfmSlice = ofmConn->slice;
                newOfmSlice.offset += Shape(by * BH, bx * BW, bc * BC);
                auto &newOfmShape = newOfmSlice.shape;
                newOfmSlice.shape = Shape::Max(
                    Shape::Min(newOfmShape - Shape(by * BH, bx * BW, bc * BC), Shape(BH, BW, BC)), newOfmShape.WithOnes());
                std::unique_ptr<SchedulerOperation> subOp = MakeSubOperation(op.get());
                auto *subIfmConn = subOp->IFM(0);
                subIfmConn->slice = std::move(newIfmSlice);
                if ( ifm2Conn )
                {
                    auto *subIfm2Conn = subOp->IFM(1);
                    subIfm2Conn->slice = std::move(newIfm2Slice);
                }
                auto *subOfmConn = subOp->OFM();
                subOfmConn->slice = std::move(newOfmSlice);
                auto subOps = doDecompose(arch, std::move(subOp));
                result.insert(result.end(), std::make_move_iterator(subOps.begin()), std::make_move_iterator(subOps.end()));
            }
        }
    }
    return result;
}

// Decompose to sub-operations in slices along the specified axis.
static std::vector<std::unique_ptr<SchedulerOperation>> DecomposeLargeAxis(int axis, int sliceSize, Architecture *arch,
    std::unique_ptr<SchedulerOperation> op, const DecomposeFunc &doDecompose)
{
    std::vector<std::unique_ptr<SchedulerOperation>> result;
    auto *ofmConn = op->Output(TensorUsage::OFM);
    auto *ifmConn = op->Input(TensorUsage::IFM0);
    auto *ifm2Conn = op->TryInput(TensorUsage::IFM1);

    static auto SliceFunc = [](SchedulerConnection *conn, int ax, int maxSlice, int offset) -> TensorSlice
    {
        Shape newOffset = conn->slice.offset;
        Shape newShape = conn->SliceShape();
        // maxIndex is the largest index of the undecomposed slice
        int maxIndex = newOffset[ax] + newShape[ax];
        // Don't offset broadcasted axis
        if ( newShape[ax] != 1 )
        {
            // clamp slices if they exceed maxIndex
            newOffset[ax] = std::min(newOffset[ax] + offset, maxIndex - 1);
            newShape[ax] = std::min(maxSlice, maxIndex - newOffset[ax]);
        }
        assert(newOffset[ax] + newShape[ax] <= maxIndex);
        newOffset = newOffset.Permute(uint32_t(conn->transpose));
        newShape = newShape.Permute(uint32_t(conn->transpose));
        return {newOffset, newShape};
    };

    auto axisSize = ofmConn->SliceShape()[axis];
    for ( int i = 0; i < axisSize; i += sliceSize )
    {
        std::unique_ptr<SchedulerOperation> subOp = MakeSubOperation(op.get());
        subOp->Input(TensorUsage::IFM0)->slice = SliceFunc(ifmConn, axis, sliceSize, i);
        subOp->Output(TensorUsage::OFM)->slice = SliceFunc(ofmConn, axis, sliceSize, i);
        if ( ifm2Conn )
        {
            subOp->Input(TensorUsage::IFM1)->slice = SliceFunc(ifm2Conn, axis, sliceSize, i);
        }
        auto subOps = doDecompose(arch, std::move(subOp));
        result.insert(result.end(), std::make_move_iterator(subOps.begin()), std::make_move_iterator(subOps.end()));
    }
    return result;
}

// Decompose to sub-operations with size 1 along the leading <dimension> axes.
// Used for the batch dimension, and for the leading N-3 dimensions for elementwise operations.
static std::vector<std::unique_ptr<SchedulerOperation>> DecomposeLeadingDimensions(
    int dimensions, Architecture *arch, std::unique_ptr<SchedulerOperation> op, const DecomposeFunc &doDecompose)
{
    int axis = dimensions - 1;
    // Use a callback-mechanism to recurse over all leading dimensions
    DecomposeFunc cb = [axis, &doDecompose](Architecture *_arch, std::unique_ptr<SchedulerOperation> _op)
    {
        if ( axis > 0 )
        {
            return DecomposeLeadingDimensions(axis, _arch, std::move(_op), doDecompose);
        }
        return doDecompose(_arch, std::move(_op));
    };

    return DecomposeLargeAxis(axis, 1, arch, std::move(op), cb);
}

// Handle dilation by decomposing to suboperations with input stride = dilation and dilation 1
static std::vector<std::unique_ptr<SchedulerOperation>>
HandleDilation(Architecture *arch, std::unique_ptr<SchedulerOperation> op, const DecomposeFunc &doDecompose)
{
    std::vector<std::unique_ptr<SchedulerOperation>> result;
    auto *ofmConn = op->Output(TensorUsage::OFM);
    auto *ifmConn = op->Input(TensorUsage::IFM);
    auto *kernel = op->Kernel();
    auto &dilation = kernel->Dilation();
    auto &stride = kernel->Stride();
    auto GY = std::gcd(dilation.y, stride.y);
    auto GX = std::gcd(dilation.x, stride.x);
    auto newStride = stride / Point2i{GX, GY};
    auto DY = dilation.y / GY;
    auto DX = dilation.x / GX;
    for ( auto dy = 0; dy < DY; ++dy )
    {
        for ( auto dx = 0; dx < DX; ++dx )
        {
            auto newIfmSlice = ifmConn->slice;
            auto newOfmSlice = ofmConn->slice;
            auto ifmStrides = ifmConn->stepXY;
            auto ofmStrides = ofmConn->stepXY;
            newIfmSlice.offset =
                newIfmSlice.offset.WithHeight(newIfmSlice.offset.Height() + dy * GY * newStride.y)
                    .WithWidth(newIfmSlice.offset.Width() + dx * GX * newStride.x);
            ifmStrides.y *= DY * GY;
            ifmStrides.x *= DX * GX;
            newOfmSlice.offset =
                newOfmSlice.offset.WithHeight(newOfmSlice.offset.Height() + dy).WithWidth(newOfmSlice.offset.Width() + dx);
            newOfmSlice.shape =
                newOfmSlice.shape.WithHeight(newOfmSlice.shape.Height() - dy).WithWidth(newOfmSlice.shape.Width() - dx);
            if ( newOfmSlice.shape.Width() > 0 && newOfmSlice.shape.Height() > 0 )
            {
                ofmStrides.y *= DY;
                ofmStrides.x *= DX;
                auto newKernel = kernel->WithDilation({1, 1}).WithStride(newStride);
                std::unique_ptr<SchedulerOperation> subOp = MakeSubOperation(op.get(), &newKernel);
                auto *subIfmConn = subOp->Input(TensorUsage::IFM);
                subIfmConn->slice = std::move(newIfmSlice);
                subIfmConn->stepXY = ifmStrides;
                auto *subOfmConn = subOp->Output(TensorUsage::OFM);
                subOfmConn->slice = std::move(newOfmSlice);
                subOfmConn->stepXY = ofmStrides;
                if ( subOp->AccumulatorMode().source == AccumulatorSource::Ifm2 )
                {
                    auto *subIfm2Conn = subOp->Input(TensorUsage::IFM1);
                    subIfm2Conn->slice.shape = subOfmConn->slice.shape;
                    subIfm2Conn->slice.offset = subIfm2Conn->slice.shape.WithZeros().WithHW(
                        subOfmConn->slice.offset.Height(), subOfmConn->slice.offset.Width());
                    subIfm2Conn->stepXY = subOfmConn->stepXY;
                }
                auto subOps = doDecompose(arch, std::move(subOp));
                result.insert(result.end(), std::make_move_iterator(subOps.begin()), std::make_move_iterator(subOps.end()));
            }
        }
    }
    return result;
}

static Margin NewPaddingForBlock(const Margin &padding, const Shape &offset, const Shape &ifmShape, const Shape &block,
    const Point2i &stride, const Point2i &kernelSize)
{
    Point2i unpaddedOffset = {offset.Width() > 0 ? offset.Width() : 0, offset.Height() > 0 ? offset.Height() : 0};
    int top = std::max(padding.Top() - unpaddedOffset.y, 0);
    int left = std::max(padding.Left() - unpaddedOffset.x, 0);
    int remainingWidth = std::max(ifmShape.Width() - (unpaddedOffset.x + block.Width()) * stride.x - (kernelSize.x - 1), 0);
    int remainingHeight = std::max(ifmShape.Height() - (unpaddedOffset.y + block.Height()) * stride.y - (kernelSize.y - 1), 0);
    int bottom = std::max(padding.Bottom() - remainingHeight, 0);
    int right = std::max(padding.Right() - remainingWidth, 0);
    return Margin(top, left, bottom, right);
}

static void UpdatePaddingAndIfmOffset(SchedulerOperation *op)
{
    auto *kernel = op->Kernel();
    auto &padding = kernel->Padding();
    auto &ifmSlice = op->Input(TensorUsage::IFM)->slice;
    // Negative ifm offsets indicate new padding values with ifm offset 0
    auto topPad = std::max(0, -ifmSlice.offset.Height());
    auto leftPad = std::max(0, -ifmSlice.offset.Width());
    auto newHeight = std::max(0, ifmSlice.offset.Height());
    auto newWidth = std::max(0, ifmSlice.offset.Width());
    ifmSlice.offset = ifmSlice.offset.WithHeight(newHeight).WithWidth(newWidth);
    auto newPadding = Margin(topPad, leftPad, padding.Bottom(), padding.Right());
    auto newKernel = kernel->WithPadding(newPadding);
    op->SetKernel(newKernel);
}

// Return a slice of a tensor
template<typename SRC_TYPE, typename DST_TYPE = SRC_TYPE>
static std::shared_ptr<SchedulerTensor>
SliceT(SchedulerTensor *tensor, const Shape &offset, const Shape &shape, const Shape &readShape, const Point2i &stepXY)
{
    constexpr int MAX_RANK = 5;
    assert(shape.Size() <= MAX_RANK);
    assert(offset.Size() <= MAX_RANK);
    auto paddedInShape = Shape::PadAxes(readShape ? readShape : tensor->bufferView.ViewShape(), shape.Size(), 1);
    const auto &inBufferView = tensor->bufferView.Reshape(paddedInShape).SubView(offset, shape);
    const auto &inBufferValues = inBufferView.Values<SRC_TYPE, DST_TYPE>();

    // Create output buffer that will contain the slice
    const auto size = shape.Elements();
    auto outBuffer = std::make_shared<Buffer>(std::make_unique<DST_TYPE[]>(size), size);
    BufferView outBufferView(std::move(outBuffer), 0, 8 * sizeof(DST_TYPE), shape, {});
    auto outBufferValues = outBufferView.WritableValues<DST_TYPE>();

    // Copy values into the output buffer
    auto paddedOutShape = Shape::PadAxes(shape, MAX_RANK, 1);
    auto ndhwc = paddedOutShape.WithZeros();
    for ( ndhwc[0] = 0; ndhwc[0] < paddedOutShape[0]; ndhwc[0]++ )
    {
        for ( ndhwc[1] = 0; ndhwc[1] < paddedOutShape[1]; ndhwc[1]++ )
        {
            for ( ndhwc[2] = 0; ndhwc[2] < paddedOutShape[2]; ndhwc[2] += stepXY.y )
            {
                for ( ndhwc[3] = 0; ndhwc[3] < paddedOutShape[3]; ndhwc[3] += stepXY.x )
                {
                    for ( ndhwc[4] = 0; ndhwc[4] < paddedOutShape[4]; ndhwc[4]++ )
                    {
                        Shape pos(ndhwc, shape.Size());
                        outBufferValues[pos] = inBufferValues[pos];
                    }
                }
            }
        }
    }

    // Clone tensor with new buffer with new unique ID because now the tensor is different
    auto clonedTensor = tensor->Clone();
    clonedTensor->bufferView = std::move(outBufferView);
    clonedTensor->storageShape = shape;

    return clonedTensor;
}

// Return a slice of a tensor
static std::shared_ptr<SchedulerTensor>
Slice(SchedulerTensor *tensor, const Shape &offset, const Shape &shape, Shape readShape = {}, Point2i stepXY = {1, 1})
{
    assert(tensor->IsConstant());
    assert(tensor->producers.size() == 0);
    assert(!readShape || readShape.Elements() == tensor->storageShape.Elements());
    readShape = readShape ? readShape : tensor->storageShape;
    assert(Shape(offset + shape, readShape.Size(), 1) <= readShape);

    switch ( tensor->dataType )
    {
        case DataType::Int8:
            return SliceT<int8_t>(tensor, offset, shape, readShape, stepXY);
        case DataType::UInt8:
            return SliceT<uint8_t>(tensor, offset, shape, readShape, stepXY);
        case DataType::Int32:
            return SliceT<int32_t>(tensor, offset, shape, readShape, stepXY);
        case DataType::Int64:
            return SliceT<int64_t>(tensor, offset, shape, readShape, stepXY);
        case DataType::Int48:
        {
            auto slice = SliceT<int48_t, int64_t>(tensor, offset, shape, readShape, stepXY);
            slice->dataType = DataType::Int64;
            return slice;
        }
        default:
            assert(false && "Unknown data type");
            return nullptr;
    }
}

static Shape NewOfmBlockShape(Architecture *arch, SchedulerOperation *op)
{
    // Find a block shape for decomposition that will fit in accumulator RAM,
    // and where ifm also fits.
    // GetOpConfig finds a block that fulfills this.
    // TODO: MLBEDSW-9860
    // If block decomposition is needed just because of too large ifm/ofm dimension,
    // a larger block size could potentially be used.
    // For a 1x1 kernel without ifm/ofm size above the limit, no block decomposition is needed,
    // as accumulators do not need to be retained.

    Shape newBlock;
    auto ofmShape = op->OFM()->SliceShape();
    auto kernel = *op->Kernel();
    // Get block config for the op after decomposition to smaller kernel
    // Avoids problems where a block config can't be found as ifm gets too big for RAM
    auto minKernel = kernel.WithSize({1, 1}).WithStride({1, 1});
    op->SetKernel(minKernel);
    auto config = GetOpConfig(arch, op);
    op->SetKernel(kernel);
    assert(config && "No config found.");
    if ( !config ) throw DecompositionFailure("No config found");
    auto HW = config->OptimalStripeGranule();
    Shape configBlock = ofmShape.WithBatch(1).WithHW(HW.y, HW.x).WithDepth(config->OptimalDepthGranule());
    if ( Shape::Min(ofmShape, configBlock) != ofmShape )
    {
        newBlock = Shape::Min(ofmShape, configBlock);
    }
    return newBlock;
}

// Decompose into smaller blocks
static std::vector<std::unique_ptr<SchedulerOperation>>
DecomposeBlocks(Architecture *arch, std::unique_ptr<SchedulerOperation> op, Shape &blockShape, DecomposeFunc doDecompose)
{
    std::vector<std::unique_ptr<SchedulerOperation>> result;
    auto BH = blockShape.Height();
    auto BW = blockShape.Width();
    auto BC = blockShape.Depth();
    auto *ofmConn = op->Output(TensorUsage::OFM);
    auto *ifmConn = op->Input(TensorUsage::IFM);
    auto *kernel = op->Kernel();
    auto stride = kernel->Stride();
    const auto &padding = kernel->Padding();
    auto &ofmShape = ofmConn->SliceShape();
    const auto NC = DivRoundUp(ofmShape.Depth(), blockShape.Depth());
    auto ofmOffset = ofmConn->slice.offset;
    // Need to align the start of each block with the ofm steps
    auto stepY = DivRoundUp(BH, ofmConn->stepXY.y) * ofmConn->stepXY.y;
    auto stepX = DivRoundUp(BW, ofmConn->stepXY.x) * ofmConn->stepXY.x;
    auto ifmstepY = stepY * ifmConn->stepXY.y / ofmConn->stepXY.y * stride.y;
    auto ifmstepX = stepX * ifmConn->stepXY.x / ofmConn->stepXY.x * stride.x;
    auto ofmEnd = ofmOffset + ofmShape;
    auto ofmStep = ofmOffset.WithZeros().WithHeight(stepY).WithWidth(stepX);
    auto ifmStep = ofmStep.WithHeight(ifmstepY).WithWidth(ifmstepX);
    auto ifmOffset = ifmConn->slice.offset;
    while ( ofmOffset.Height() < ofmConn->slice.offset.Height() + ofmConn->SliceShape().Height() )
    {
        auto ifmOffsetWidth = ifmOffset.Width();
        auto ofmOffsetWidth = ofmOffset.Width();
        while ( ofmOffset.Width() < ofmConn->slice.offset.Width() + ofmConn->SliceShape().Width() )
        {
            for ( auto bc = 0; bc < NC; bc++ )
            {
                auto newIfmSlice = ifmConn->slice;
                newIfmSlice.offset = Shape::Min(ifmOffset, ifmConn->shape);
                auto newOfmSlice = ofmConn->slice;
                newOfmSlice.offset = ofmOffset.WithDepth(ofmOffset.Depth() + bc * BC);
                auto &newOfmShape = ofmConn->SliceShape();
                auto newOfmHeight = std::min(ofmEnd.Height() - ofmOffset.Height(), BH);
                auto newOfmWidth = std::min(ofmEnd.Width() - ofmOffset.Width(), BW);
                auto newOfmDepth = std::min(ofmEnd.Depth() - bc * BC, BC);

                newOfmSlice.shape = newOfmShape.WithHeight(newOfmHeight).WithWidth(newOfmWidth).WithDepth(newOfmDepth);
                if ( !newOfmSlice.shape.Elements() ) continue;
                // Compensate for negative offset (i.e. padding)
                auto ifmBlockWidth = ifmStep.Width() + (newIfmSlice.offset.Width() < 0 ? newIfmSlice.offset.Width() : 0);
                auto ifmBlockHeight = ifmStep.Height() + (newIfmSlice.offset.Height() < 0 ? newIfmSlice.offset.Height() : 0);
                if ( ofmStep.Width() >= ofmConn->SliceShape().Width() ) ifmBlockWidth = ifmConn->SliceShape().Width();
                if ( ofmStep.Height() >= ofmConn->SliceShape().Height() )
                    ifmBlockHeight = ifmConn->SliceShape().Height();
                newIfmSlice.shape =
                    ifmConn->SliceShape()
                        .WithWidth(std::min(ifmBlockWidth, ifmConn->shape.Width() - newIfmSlice.offset.Width()))
                        .WithHeight(std::min(ifmBlockHeight, ifmConn->shape.Height() - newIfmSlice.offset.Height()));
                Margin newPadding = NewPaddingForBlock(
                    padding, newIfmSlice.offset, ifmConn->shape, blockShape, stride, kernel->Size());
                auto newKernel = kernel->WithPadding(newPadding);
                std::unique_ptr<SchedulerOperation> subOp = MakeSubOperation(op.get(), &newKernel);
                auto *subIfmConn = subOp->Input(TensorUsage::IFM);
                subIfmConn->slice = std::move(newIfmSlice);
                auto *subOfmConn = subOp->Output(TensorUsage::OFM);
                subOfmConn->slice = std::move(newOfmSlice);
                // Decomposition algorithm has weight slicing here if NC > 1, new_weights[oc,y,x,ic] =
                // weights[oc+bc*NC,y,x,ic] Handled by the existing weight slicing code in the scheduler, so not done
                // here.

                if ( subOp->Output(TensorUsage::OFM)->SliceShape().Elements() )
                {
                    auto subOps = doDecompose(arch, std::move(subOp));
                    result.insert(result.end(), std::make_move_iterator(subOps.begin()), std::make_move_iterator(subOps.end()));
                }
            }
            ifmOffset = ifmOffset.WithWidth(ifmOffset.Width() + ifmStep.Width());
            ofmOffset = ofmOffset.WithWidth(ofmOffset.Width() + ofmStep.Width());
        }
        ifmOffset = ifmOffset.WithHeight(ifmOffset.Height() + ifmStep.Height()).WithWidth(ifmOffsetWidth);
        ofmOffset = ofmOffset.WithHeight(ofmOffset.Height() + ofmStep.Height()).WithWidth(ofmOffsetWidth);
    }
    return result;
}

// Handle large strides by decomposing to suboperations with saved accumulators
static std::vector<std::unique_ptr<SchedulerOperation>>
DecomposeForStrides(Architecture *arch, std::unique_ptr<SchedulerOperation> op, DecomposeFunc doDecompose)
{
    std::vector<std::unique_ptr<SchedulerOperation>> result;

    auto *weightsConn = op->TryInput(TensorUsage::Weights);
    auto *ofmConn = op->Output(TensorUsage::OFM);
    auto *ifmConn = op->Input(TensorUsage::IFM);
    auto *kernel = op->Kernel();
    auto &stride = kernel->Stride();
    auto &kernelSize = kernel->Size();
    auto SY = stride.y;
    auto SX = stride.x;

    const int MAX_KERNEL_X = std::numeric_limits<uint16_t>::max();
    const int MAX_KERNEL_Y = std::numeric_limits<uint16_t>::max();
    const int MAX_IFM_DEPTH = std::numeric_limits<uint16_t>::max();
    auto ifm_depth = ifmConn->slice.shape.Depth();
    bool didSendOne = false;
    AccumulatorControl accMode = {AccumulatorSource::Acc, false};
    for ( auto ky = 0; ky < kernelSize.y; ky++ )
    {
        for ( auto kx = 0; kx < kernelSize.x; kx++ )
        {
            auto newIfmSlice = ifmConn->slice;
            auto ifmStrides = ifmConn->stepXY;
            newIfmSlice.offset =
                newIfmSlice.offset.WithHeight(newIfmSlice.offset.Height() + ky * ifmConn->stepXY.y)
                    .WithWidth(newIfmSlice.offset.Width() + kx * ifmConn->stepXY.x);
            // If ifm slice shape was reduced from the block size due to padding,
            // it needs to be increased again as we step past some padding.
            auto extendMax = Point2i{0, 0} - Point2i::Min(ifmConn->slice.offset.WH<int>(), {0, 0});
            auto extend = Point2i::Min(ifmConn->stepXY * Point2i{kx, ky}, extendMax);
            newIfmSlice.shape =
                newIfmSlice.shape
                    .WithHeight(std::max(0,
                        std::min(ifmConn->shape.Height() - newIfmSlice.offset.Height(),
                            newIfmSlice.shape.Height() + extend.y)))
                    .WithWidth(std::max(0,
                        std::min(ifmConn->shape.Width() - newIfmSlice.offset.Width(), newIfmSlice.shape.Width() + extend.x)));
            ifmStrides.y *= SY;
            ifmStrides.x *= SX;
            // Don't generate an op that will only produce zeros, unless it is the last one in the group,
            // and we have not sent one before.
            if ( ky < (kernelSize.y - 1) || kx < (kernelSize.x - 1) || didSendOne )
            {
                // Find if the slice reads elements inside the IFM (not counting the padded-area)
                // for a positive offset this is at least one as long as the shape has nonZero volume
                if ( newIfmSlice.shape.Elements64() <= 0 )
                {
                    // zero-volume read-shape
                    continue;
                }
                // for a negative offset (which should be interpreted as left/top padding)
                // we need to account for ifmStrides and compute the first positive offset
                if ( newIfmSlice.offset.Height() < 0 )
                {
                    // Find first positive coordinate and check whether it is inside the slice
                    int firstH = (newIfmSlice.offset.Height() % ifmStrides.y);
                    if ( firstH < 0 )
                    {
                        firstH += ifmStrides.y;
                    }
                    if ( firstH >= newIfmSlice.shape.Height() )
                    {
                        // First positive coordinate results in zero volume
                        continue;
                    }
                }
                else if ( newIfmSlice.offset.Width() < 0 )
                {
                    // Find first positive coordinate results in zero volume
                    int firstW = (newIfmSlice.offset.Width() % ifmStrides.x);
                    if ( firstW < 0 )
                    {
                        firstW += ifmStrides.x;
                    }
                    if ( firstW >= newIfmSlice.shape.Width() )
                    {
                        // First positive coordinate is outside of the slice-shape
                        continue;
                    }
                }
            }
            Point2i ifmPoints =
                DivRoundUp((Point2i{newIfmSlice.shape.Width(), newIfmSlice.shape.Height()} +
                               Point2i{kernel->Padding().Left(), kernel->Padding().Top()}),
                    ifmStrides) -
                Point2i{1, 1};
            const auto newHeight = 1;
            const auto newWidth = 1;
            auto weightOffsetXY = Point2i::Min(Point2i{kx, ky}, kernelSize - Point2i{1, 1});
            // New weights for the reduced kernel. No need to slice in depth here.
            // TODO: MLBEDSW-9861
            // We are creating many identical weight slices here, need to add caching unless we implement
            // TensorConnection slice support for weights, MLBEDSW-9267
            TensorSlice weightSlice;
            if ( weightsConn )
            {
                weightSlice.offset =
                    weightsConn->SliceShape().WithZeros().WithHeight(weightOffsetXY.y).WithWidth(weightOffsetXY.x);
                weightSlice.shape = weightsConn->SliceShape().WithHeight(newHeight).WithWidth(newWidth);
            }
            auto weightStepXY = Point2i{SX, SY};
            auto newKernel = kernel->WithStride({1, 1}).WithSize({newWidth, newHeight});
            std::unique_ptr<SchedulerOperation> subOp = MakeSubOperation(op.get(), &newKernel);
            subOp->RemoveInput(TensorUsage::IFM1);  // Remove acc input
            auto *subIfmConn = subOp->Input(TensorUsage::IFM);
            subIfmConn->slice = std::move(newIfmSlice);
            subIfmConn->stepXY = ifmStrides;
            if ( weightsConn && ((weightSlice.offset.WH<int>() != Point2i(0, 0)) || weightSlice.shape < weightsConn->SliceShape()) )
            {
                auto *subWeightsConn = subOp->Input(TensorUsage::Weights);
                subWeightsConn->tensor = Slice(weightsConn->tensor.get(), weightSlice.offset, weightSlice.shape, {}, weightStepXY);
                subWeightsConn->tensor->consumers.push_back(subOp.get());
                subWeightsConn->shape = weightSlice.shape;
            }
            subOp->SetAccumulatorMode(accMode);
            auto subOps = doDecompose(arch, std::move(subOp));
            result.insert(result.end(), std::make_move_iterator(subOps.begin()), std::make_move_iterator(subOps.end()));
            didSendOne = true;
        }
    }
    accMode = result.back()->AccumulatorMode();
    accMode.outputEnabled = true;
    result.back()->SetAccumulatorMode(accMode);
    accMode = result.front()->AccumulatorMode();
    accMode.source = op->AccumulatorMode().source;
    result.front()->SetAccumulatorMode(accMode);
    // Reconnect acc input
    if ( accMode.source == AccumulatorSource::Ifm2 )
    {
        auto subOpIfm2 = result.front()->AddInput(TensorUsage::IFM1);
        *subOpIfm2 = *op->Input(TensorUsage::IFM1);
        subOpIfm2->tensor->consumers.push_back(result.front().get());
    }
    return result;
}

std::vector<std::unique_ptr<SchedulerOperation>> DecomposeConv2D(Architecture *arch, std::unique_ptr<SchedulerOperation> op)
{
    std::vector<std::unique_ptr<SchedulerOperation>> result;
    auto *ofmConn = op->Output(TensorUsage::OFM);
    auto *ifmConn = op->Input(TensorUsage::IFM);
    const auto &ofmShape = ofmConn->SliceShape();
    const auto &ifmShape = ifmConn->SliceShape();
    auto &ofmSlice = ofmConn->slice;
    auto &ifmSlice = ifmConn->slice;
    auto *kernel = op->Kernel();
    auto &padding = kernel->Padding();
    ofmSlice.Initialize(ofmShape.WithZeros(), ofmShape);
    ifmSlice.Initialize(ifmShape.WithZeros().WithHW(-padding.Top(), -padding.Left()), ifmShape);

    if ( ofmShape.Batch() > 1 )
    {
        return DecomposeLeadingDimensions(1, arch, std::move(op), DecomposeConv2D);
    }
    if ( !NeedsDecompose(arch, op.get()) )
    {
        UpdatePaddingAndIfmOffset(op.get());
        result.emplace_back(std::move(op));
        return result;
    }
    auto &dilation = kernel->Dilation();
    if ( dilation.x > 1 || dilation.y > 1 )
    {
        return HandleDilation(arch, std::move(op), DecomposeConv2D);
    }
    try
    {
        if ( auto newBlockShape = NewOfmBlockShape(arch, op.get()) )
        {
            return DecomposeBlocks(arch, std::move(op), newBlockShape, DecomposeConv2D);
        }
    }
    catch ( const DecompositionFailure & )
    {
        UpdatePaddingAndIfmOffset(op.get());
        result.emplace_back(std::move(op));
        return result;
    }

    if ( arch->Constraints()->SupportsAccumulatorSaveRestore() &&
         op->Input(TensorUsage::Weights)->tensor->IsConstant() && op->Kernel()->Stride().AreaXY() > 1 )
    {
        return DecomposeForStrides(arch, std::move(op), DecomposeConv2D);
    }
    // If we get here, decomposition has failed, the resulting operations will be executed on CPU
    UpdatePaddingAndIfmOffset(op.get());
    result.emplace_back(std::move(op));
    return result;
}

std::vector<std::unique_ptr<SchedulerOperation>> DecomposeConv3D(Architecture *arch, std::unique_ptr<SchedulerOperation> op)
{
    std::vector<std::unique_ptr<SchedulerOperation>> result;
    auto *ofmConn = op->Output(TensorUsage::OFM);
    auto *ifmConn = op->Input(TensorUsage::IFM);
    auto *weightsConn = op->Input(TensorUsage::Weights);
    const auto &ofmShape = ofmConn->SliceShape();
    const auto &ifmShape = ifmConn->SliceShape();
    auto &ofmSlice = ofmConn->slice;
    auto &ifmSlice = ifmConn->slice;
    auto *kernel = op->Kernel();
    auto &padding = kernel->Padding();
    ofmSlice.Initialize(ofmShape.WithZeros(), ofmShape);
    ifmSlice.Initialize(ifmShape.WithZeros(), ifmShape);

    if ( ofmShape[0] > 1 )  // Batch
    {
        return DecomposeLeadingDimensions(1, arch, std::move(op), DecomposeConv3D);
    }
    const int OD = ofmSlice.shape[1];
    const int ID = ifmSlice.shape[1];
    const int KD = kernel->Size3D().z;
    if ( (arch->Constraints()->SupportsAccumulatorSaveRestore() || KD == 1) && weightsConn->tensor->IsConstant() )
    {
        auto InitConnection = [](SchedulerConnection *dst, SchedulerConnection *src, int dOffset, int dSize)
        {
            dst->shape = Shape(src->SliceShape(), 4);
            // Handle batch
            dst->shape[0] *= src->shape[0];
            dst->slice.offset = dst->shape.WithZeros().WithBatch(src->slice.offset[0] * dSize + dOffset);
            dst->slice.shape = dst->shape.WithBatch(1);
        };
        // Create SchedulerTensor for ACC
        auto acc = std::make_shared<SchedulerTensor>();
        acc->uid = GenerateUniqueId();
        acc->memArea = ofmConn->tensor->memArea;
        acc->dataType = ifmConn->Type() == DataType::Int16 ? DataType::Int64 : DataType::Int32;
        acc->storageShape = Shape(ofmShape, 4).WithBatch(1);
        // Create ifm zero point SchedulerTensor, only needed for broadcast
        // Setup is done below if needed
        auto ifm0 = std::make_shared<SchedulerTensor>();
        for ( int od = 0; od < OD; od++ )
        {
            std::vector<std::unique_ptr<SchedulerOperation>> conv2dSubOps;
            for ( int kd = 0; kd < KD; kd++ )
            {
                const int id = od * kernel->Stride3D().z - padding.Near() + kd * kernel->Dilation3D().z;
                if ( id >= 0 && id < ID )
                {
                    auto subOp = MakeSubOperation(op.get(), nullptr, OpType::Conv2D);
                    InitConnection(subOp->Output(TensorUsage::OFM), ofmConn, od, OD);
                    InitConnection(subOp->Input(TensorUsage::IFM), ifmConn, id, ID);
                    // Update slice offset for DecomposeConv2D pad handling
                    auto subOpIfm = subOp->Input(TensorUsage::IFM);
                    subOpIfm->slice.offset = subOpIfm->slice.offset.WithHW(-padding.Top(), -padding.Left());

                    auto subOpWeights = subOp->Input(TensorUsage::Weights);
                    if ( KD > 1 )
                    {
                        auto offset = subOpWeights->shape.WithZeros().With(1, kd);
                        auto subOpWeightsSlice = Slice(subOpWeights->tensor.get(), offset, subOpWeights->shape.With(1, 1));
                        subOp->ConnectInput(TensorUsage::Weights, subOpWeightsSlice);
                    }
                    // New weight shape
                    auto subOpWeightShape = subOpWeights->shape.Erase(1);
                    subOpWeights->shape = subOpWeights->tensor->storageShape = subOpWeightShape;
                    subOpWeights->tensor->bufferView = subOpWeights->tensor->bufferView.Reshape(subOpWeightShape);

                    conv2dSubOps.emplace_back(std::move(subOp));
                }
            }
            if ( conv2dSubOps.empty() )
            {
                // Kernel in padding only area, need to broadcast bias to OFM,
                // using Rescale with bias and ifm zero point as input
                auto unitKernel = Kernel::UnitKernel();
                auto subOp = MakeSubOperation(op.get(), &unitKernel, OpType::Rescale);
                subOp->RemoveInput(TensorUsage::Weights);
                InitConnection(subOp->Output(TensorUsage::OFM), ofmConn, od, OD);

                auto subOpIfm = subOp->Input(TensorUsage::IFM);
                const auto &ifm0shape = subOp->Output(TensorUsage::OFM)->slice.shape;

                if ( ifm0->uid == INVALID_UID )
                {
                    // Setup SchedulerTensor for 0 input
                    ifm0->uid = GenerateUniqueId();
                    ifm0->dataType = subOpIfm->Type();
                    ifm0->memArea = arch->ReadonlyMemory();
                    ifm0->format = TensorFormat::NHWC;
                    const auto bufSize = ifm0shape.Elements();
                    const auto &zeroPoints = subOpIfm->quantization.zeroPoints;
                    const int64_t ifmZp = zeroPoints.empty() ? 0 : zeroPoints.front();
                    std::shared_ptr<Buffer> ifm0buf;
                    switch ( ifm0->dataType )
                    {
                        case DataType::Int8:
                            ifm0buf = std::make_shared<Buffer>(std::vector<int8_t>(bufSize, int8_t(ifmZp)));
                            break;
                        case DataType::Int16:
                            ifm0buf = std::make_shared<Buffer>(std::vector<int16_t>(bufSize, int16_t(ifmZp)));
                            break;
                        default:
                            assert(false && "Unsupported ifm data type");
                            break;
                    }
                    ifm0->bufferView = BufferView(ifm0buf, 0, DataTypeStorageSizeBits(ifm0->dataType), ifm0shape, {});
                    ifm0->storageShape = ifm0->bufferView.ViewShape();
                }
                subOp->ConnectInput(TensorUsage::IFM, ifm0);
                subOpIfm->shape = ifm0shape;
                subOpIfm->slice.offset = ifm0shape.WithZeros();
                subOpIfm->slice.shape = ifm0shape;

                auto subOps = DecomposeElementwise(arch, std::move(subOp));
                result.insert(result.end(), std::make_move_iterator(subOps.begin()), std::make_move_iterator(subOps.end()));
            }
            else if ( conv2dSubOps.size() > 1 )
            {
                auto &tail = conv2dSubOps.back();
                auto bias = tail->Input(TensorUsage::Scales);

                // Create SchedulerTensor for 0 (no) bias
                auto bias0 = bias->tensor->Clone();
                auto bias0buf = std::make_shared<Buffer>(Buffer::ConstValue<int64_t>(0));
                assert(DataTypeStorageSizeBits(bias0->dataType) <= int(8 * sizeof(int64_t)));
                bias0->bufferView = BufferView(bias0buf, 0, DataTypeStorageSizeBits(bias0->dataType), {1}, {});
                bias0->storageShape = bias0->bufferView.ViewShape();

                for ( auto subOp = conv2dSubOps.begin(); subOp != conv2dSubOps.end(); ++subOp )
                {
                    if ( subOp != conv2dSubOps.begin() )
                    {
                        // Acc source ifm2 for all but first subop
                        (*subOp)->ConnectInput(TensorUsage::IFM1, acc)->shape = acc->storageShape;
                        (*subOp)->SetAccumulatorMode({AccumulatorSource::Ifm2, true});
                    }
                    if ( *subOp != tail )
                    {
                        // Remove scaling and bias and set ofm = acc tensor
                        // (used as acc input for next op) for all but last subop
                        auto subOpOfm = (*subOp)->ConnectOutput(TensorUsage::OFM, acc);
                        auto subOpIfm = (*subOp)->IFM(0);
                        auto subOpWeights = (*subOp)->Input(TensorUsage::Weights);
                        auto subOpBias = (*subOp)->ConnectInput(TensorUsage::Scales, bias0);
                        subOpOfm->shape = acc->storageShape;
                        subOpOfm->slice.offset = subOpOfm->shape.WithZeros();
                        subOpOfm->quantization.scales = {QuantizedScale::Unit()};
                        subOpIfm->quantization.scales = {QuantizedScale::Unit()};
                        subOpWeights->quantization.scales = {QuantizedScale::Unit()};
                        subOpBias->shape = bias0->storageShape;
                    }
                }
            }
            auto end = std::make_move_iterator(conv2dSubOps.end());
            for ( auto subOp = std::make_move_iterator(conv2dSubOps.begin()); subOp != end; ++subOp )
            {
                auto subOps = DecomposeConv2D(arch, *subOp);
                result.insert(result.end(), std::make_move_iterator(subOps.begin()), std::make_move_iterator(subOps.end()));
            }
        }
        return result;
    }
    // If we get here, decomposition has failed, the resulting operations will be executed on CPU
    result.emplace_back(std::move(op));
    return result;
}

std::vector<std::unique_ptr<SchedulerOperation>> DecomposeDepthwiseConv2D(Architecture *arch, std::unique_ptr<SchedulerOperation> op)
{
    std::vector<std::unique_ptr<SchedulerOperation>> result;
    auto *ofmConn = op->Output(TensorUsage::OFM);
    auto *ifmConn = op->Input(TensorUsage::IFM);
    auto *weightsConn = op->Input(TensorUsage::Weights);
    auto *biasConn = op->Input(TensorUsage::Scales);
    const auto &ofmShape = ofmConn->SliceShape();
    const auto &ifmShape = ifmConn->SliceShape();
    const auto &weightsShape = weightsConn->shape;
    const auto &biasShape = biasConn->shape;
    auto &ofmSlice = ofmConn->slice;
    auto &ifmSlice = ifmConn->slice;
    auto *kernel = op->Kernel();
    auto &padding = kernel->Padding();
    const int depthMultiplier = kernel->DepthMultiplier();
    ofmSlice.Initialize(ofmShape.WithZeros(), ofmShape);
    ifmSlice.Initialize(ifmShape.WithZeros().WithHW(-padding.Top(), -padding.Left()), ifmShape);

    if ( ofmShape.Batch() > 1 )
    {
        return DecomposeLeadingDimensions(1, arch, std::move(op), DecomposeDepthwiseConv2D);
    }
    if ( depthMultiplier > 1 )
    {
        int subOfmDepth = ofmConn->shape.Depth() / depthMultiplier;
        // Clone ofm tensor with new unique ID for intermediate transposed result
        auto transposedOfm = ofmConn->tensor->Clone();
        transposedOfm->storageShape = ofmShape.WithBatch(depthMultiplier).WithDepth(subOfmDepth);

        // Copies quantization information and slices channels
        auto constexpr SliceQ = [](const Quantization &quantization, int offset, int step) -> Quantization
        {
            assert(offset >= 0);
            assert(step > 0);
            Quantization ret = quantization;
            if ( quantization.scales.size() > 1 )
            {
                ret.scales.clear();
                for ( size_t i = offset; i < quantization.scales.size(); i += step )
                {
                    ret.scales.push_back(quantization.scales[i]);
                }
            }
            if ( quantization.zeroPoints.size() > 1 )
            {
                ret.zeroPoints.clear();
                for ( size_t i = offset; i < quantization.zeroPoints.size(); i += step )
                {
                    ret.zeroPoints.push_back(quantization.zeroPoints[i]);
                }
            }
            return ret;
        };

        for ( int multiplier = 0; multiplier < depthMultiplier; multiplier++ )
        {
            auto newKernel = kernel->WithDepthMultiplier(1);
            auto subOp = MakeSubOperation(op.get(), &newKernel);
            auto subWeightsReadShape = Shape(kernel->Size().y, kernel->Size().x, subOfmDepth, depthMultiplier);
            auto subWeightsShape = subWeightsReadShape.WithDepth(1);
            auto subWeightOffset = weightsShape.WithZeros().WithDepth(multiplier);
            auto subWeights = Slice(weightsConn->tensor.get(), subWeightOffset, subWeightsShape, subWeightsReadShape);
            auto subWeightsConn = subOp->ConnectInput(TensorUsage::Weights, subWeights);
            // Tensor is now in AxisOrder::HWCM with M=1
            subWeightsConn->tensor->srcTensor->SetAxisOrder(AxisOrder::HWCM);
            subWeightsConn->shape = subWeightsShape;
            subWeightsConn->quantization = SliceQ(subWeightsConn->quantization, multiplier, depthMultiplier);
            if ( biasShape.Depth() > 1 )
            {
                auto subBiasReadShape = Shape(subOfmDepth, depthMultiplier);
                auto subBiasShape = Shape(subBiasReadShape.WithDepth(1), biasShape.Size(), 1);
                auto subBiasOffset = biasShape.WithZeros().WithDepth(multiplier);
                auto subBias = Slice(biasConn->tensor.get(), subBiasOffset, subBiasShape, subBiasReadShape);
                auto subBiasConn = subOp->ConnectInput(TensorUsage::Scales, subBias);
                subBiasConn->tensor->bufferView = subBiasConn->tensor->bufferView.Reshape({subOfmDepth});
                subBiasConn->shape = biasShape.WithDepth(subOfmDepth);
                subBiasConn->quantization = SliceQ(subBiasConn->quantization, multiplier, depthMultiplier);
            }
            auto subOfmConn = subOp->ConnectOutput(TensorUsage::OFM, transposedOfm);
            subOfmConn->shape = transposedOfm->storageShape;
            subOfmConn->slice.offset = ofmShape.WithZeros().WithBatch(multiplier);
            subOfmConn->slice.shape = ofmShape.WithDepth(subOfmDepth);
            subOfmConn->quantization = SliceQ(subOfmConn->quantization, multiplier, depthMultiplier);
            auto subOps = DecomposeDepthwiseConv2D(arch, std::move(subOp));
            result.insert(result.end(), std::make_move_iterator(subOps.begin()), std::make_move_iterator(subOps.end()));
        }
        // Need to transpose result [N, H, W, C] -> [H, W, C, N] (and reshape -> [1, H, W, N*C])
        auto transposeOpOfm = ofmConn->tensor;
        if ( ofmSlice.offset.Batch() )
        {  // Need to insert intermediate tensor for memory copy, since DecomposeTranspose
           // does not handle ofm slice offset
            transposeOpOfm = transposedOfm->Clone();
        }
        auto transposeOp = MakeTransposeOp(transposedOfm, transposeOpOfm, Shape(1, 2, 3, 0));
        auto subOps = DecomposeTranspose(arch, std::move(transposeOp));
        result.insert(result.end(), std::make_move_iterator(subOps.begin()), std::make_move_iterator(subOps.end()));
        if ( transposeOpOfm != ofmConn->tensor )
        {  // Insert memory copy of transposed ofm with slice offset
            auto copyOp = DecomposeElementwise(arch, MakeMemCopy(transposeOpOfm, ofmConn->tensor, &ofmSlice));
            result.insert(result.end(), std::make_move_iterator(copyOp.begin()), std::make_move_iterator(copyOp.end()));
        }
        return result;
    }

    if ( !NeedsDecompose(arch, op.get()) )
    {
        UpdatePaddingAndIfmOffset(op.get());
        result.emplace_back(std::move(op));
        return result;
    }

    // If weight tensor is in AxisOrder::HWCM (with M=1, since depthMultiplier=1 at this point),
    // reshape and set AxisOrder::IHWO with I=1, since the rest of the decomposition code
    // only handles weight tensors with AxisOrder::OHWI or AxisOrder::IHWO
    if ( weightsConn->tensor->srcTensor->AxisOrder() == AxisOrder::HWCM )
    {
        auto weightShapeIHWO = weightsConn->SliceShape().Permute(0x0321);
        weightsConn->tensor->srcTensor->SetAxisOrder(AxisOrder::IHWO);
        weightsConn->tensor->bufferView = weightsConn->tensor->bufferView.Reshape(weightShapeIHWO);
        weightsConn->tensor->storageShape = weightShapeIHWO;
        weightsConn->shape = weightShapeIHWO;
    }

    auto &dilation = kernel->Dilation();
    if ( dilation.x > 1 || dilation.y > 1 )
    {
        return HandleDilation(arch, std::move(op), DecomposeDepthwiseConv2D);
    }
    try
    {
        if ( auto newBlockShape = NewOfmBlockShape(arch, op.get()) )
        {
            return DecomposeBlocks(arch, std::move(op), newBlockShape, DecomposeDepthwiseConv2D);
        }
    }
    catch ( const DecompositionFailure & )
    {
        UpdatePaddingAndIfmOffset(op.get());
        result.emplace_back(std::move(op));
        return result;
    }

    if ( arch->Constraints()->SupportsAccumulatorSaveRestore() &&
         op->Input(TensorUsage::Weights)->tensor->IsConstant() && op->Kernel()->Stride().AreaXY() > 1 )
    {
        return DecomposeForStrides(arch, std::move(op), DecomposeDepthwiseConv2D);
    }
    // If we get here, decomposition has failed, the resulting operations will be executed on CPU
    UpdatePaddingAndIfmOffset(op.get());
    result.emplace_back(std::move(op));
    return result;
}

// Reverse elements along H and W axes
template<typename TYPE>
static std::shared_ptr<SchedulerTensor> ReverseHW2(SchedulerTensor *tensor)
{
    const auto &inBufferView = tensor->bufferView;
    const auto inBufferValues = inBufferView.Values<TYPE>();

    // Create output buffer that will contain reversed weights
    const auto size = inBufferView.Elements();
    auto outBuffer = std::make_shared<Buffer>(std::make_unique<TYPE[]>(size), size);
    BufferView outBufferView(std::move(outBuffer), tensor->bufferView);
    auto outBufferValues = outBufferView.WritableValues<TYPE>();

    // Reverse height and width into the output buffer
    int batch = outBufferView.ViewShape().Batch();
    int height = outBufferView.ViewShape().Height();
    int width = outBufferView.ViewShape().Width();
    int depth = outBufferView.ViewShape().Depth();
    for ( int n = 0; n < batch; n++ )
    {
        for ( int h = 0; h < height; h++ )
        {
            for ( int w = 0; w < width; w++ )
            {
                for ( int c = 0; c < depth; c++ )
                {
                    outBufferValues[{n, height - h - 1, width - w - 1, c}] = inBufferValues[{n, h, w, c}];
                }
            }
        }
    }

    // Clone tensor with new buffer with new unique ID because now the tensor is different
    auto clonedTensor = tensor->Clone();
    clonedTensor->bufferView = std::move(outBufferView);

    return clonedTensor;
}

// Reverse elements along H and W axes
static std::shared_ptr<SchedulerTensor> ReverseHW(SchedulerTensor *tensor)
{
    assert(tensor->IsConstant());
    assert(tensor->producers.size() == 0);

    switch ( tensor->dataType )
    {
        case DataType::Int8:
            return ReverseHW2<int8_t>(tensor);
        case DataType::UInt8:
            return ReverseHW2<uint8_t>(tensor);
        default:
            assert(false && "Unknown data type");
            return nullptr;
    }
}

// Decompose Transpose Conv2D into Conv2D
std::vector<std::unique_ptr<SchedulerOperation>> DecomposeTransposeConv2D(Architecture *arch, std::unique_ptr<SchedulerOperation> op)
{
    std::vector<std::unique_ptr<SchedulerOperation>> result;
    auto ifmConn = op->Input(TensorUsage::IFM);
    auto ofmConn = op->Output(TensorUsage::OFM);
    auto weightsConn = op->Input(TensorUsage::Weights);
    auto ifmShape = ifmConn->SliceShape();
    auto ofmShape = ofmConn->SliceShape();
    auto &ifmSlice = ifmConn->slice;
    auto &ofmSlice = ofmConn->slice;
    auto kernel = op->Kernel();
    const auto stride = kernel->Stride();
    const auto kernelSize = kernel->Size();
    assert(stride.x > 0);
    assert(stride.y > 0);
    assert(kernelSize.x > 0);
    assert(kernelSize.y > 0);

    ofmSlice.Initialize(ofmShape.WithZeros(), ofmShape);
    ifmSlice.Initialize(ifmShape.WithZeros(), ifmShape);

    if ( ofmShape.Batch() > 1 )
    {
        return DecomposeLeadingDimensions(1, arch, std::move(op), DecomposeTransposeConv2D);
    }

    // Convert TransposeConv2D to Conv2D by
    // if stride == (1,1):
    //     - reverse weights in X/Y
    // if stride == (2,2):
    //     - reverse weights in X/Y
    //     - Upsample IFM x2 by inserting zeros
    // Larger strides require decomposition: TODO MLBEDSW-9761
    if ( stride == Point2i(1, 1) || stride == Point2i(2, 2) ||
         (stride == Point2i(1, 2) && ifmShape.Width() == 1 && kernelSize.x == 1) ||
         (stride == Point2i(2, 1) && ifmShape.Height() == 1 && kernelSize.y == 1) )
    {
        if ( (stride.x == 2 || stride.y == 2) )
        {
            ifmConn->resamplingMode = ArchResampling::Zeros;
        }
        // Map to Conv2D by reversing the weights in y and x
        weightsConn->tensor = ReverseHW(weightsConn->tensor.get());
        weightsConn->tensor->consumers.push_back(op.get());
        Kernel newKernel = kernel->WithStride({1, 1});
        op->_type = OpType::Conv2D;
        op->SetKernel(newKernel);
        result.emplace_back(std::move(op));
    }
    else
    {
        // TODO MLBEDSW-9761: TransposeConv2D Large stride decomposition
        result.emplace_back(std::move(op));
    }

    return result;
}

// TODO: Move this to run prior to decomposition.
std::vector<std::unique_ptr<SchedulerOperation>> LegaliseResize(Architecture *arch, std::unique_ptr<SchedulerOperation> op)
{
    // Convert ResizeBilinear/NearestNeighbor to a number of kernel 1x1 average pools with nearest neighbor x2 upScaling
    // and a final average pool with a kernel size that depends upon the resize ops upScaling factor (x2, x4 or x8). The
    // maximum upscale factor is limited to x8 because of the limit 8x8 kernel size limit for average pool with padding.

    std::vector<std::unique_ptr<SchedulerOperation>> result;

    auto ifmConn = op->Input(TensorUsage::IFM);
    auto ofmConn = op->Output(TensorUsage::OFM);
    assert(ifmConn);
    assert(ofmConn);

    auto *attr = op->Attribute<resize_attr_t>();
    auto upscaleH = attr->scaleY.n;
    auto upscaleW = attr->scaleX.n;
    auto remainingUpscale = std::max(upscaleW, upscaleH);
    bool canLegalise = true;

    ArchRequirements req{};
    OperatorQuery(arch, op.get(), &req);
    auto reqScale = QuantizedScale(1, IntLog2(attr->scaleX.n * attr->scaleY.n));


    if ( !IsPowerOfTwo(remainingUpscale) || remainingUpscale > 8 || remainingUpscale < 2 )
    {
        canLegalise = false;
    }
    else if ( (upscaleH == 1 && ifmConn->shape.Height() != 1) || (upscaleW == 1 && ifmConn->shape.Width() != 1) )
    {
        canLegalise = false;
    }
    else if ( ofmConn->quantization.scales[0] != reqScale )
    {
        canLegalise = false;
    }

    if ( !canLegalise )
    {
        result.emplace_back(std::move(op));
        return result;
    }

    auto ofmShape = ofmConn->shape;
    auto ifmShape = ifmConn->shape;

    ofmConn->tensor->dataType = ifmConn->tensor->dataType;
    ifmConn->resamplingMode = ArchResampling::Nearest;
    // Perform 2x upScaling up to the last required
    while ( remainingUpscale > 2 )
    {
        auto newOp = std::make_unique<SchedulerOperation>(OpType::AvgPool);
        *newOp->ConnectInput(TensorUsage::IFM, ifmConn->tensor) = *ifmConn;
        std::shared_ptr<SchedulerTensor> tens = ofmConn->tensor->Clone();
        auto shape = ofmShape.WithHW(ifmConn->shape.Height() * std::min(2, upscaleH), ifmConn->shape.Width() * std::min(2, upscaleW));
        tens->storageShape = shape;
        ifmConn = newOp->ConnectOutput(TensorUsage::OFM, tens);
        ifmConn->quantization = Quantization::Unit();
        ifmConn->shape = shape;
        ifmConn->resamplingMode = ArchResampling::Nearest;
        result.emplace_back(std::move(newOp));

        remainingUpscale /= 2;
    }

    // Perform last 2x upScaling and post-processing.
    ifmConn->resamplingMode = ArchResampling::Nearest;
    auto newOp = std::make_unique<SchedulerOperation>(OpType::AvgPool);
    *newOp->ConnectInput(TensorUsage::IFM, ifmConn->tensor) = *ifmConn;

    Kernel kernel = Kernel::UnitKernel().WithPadding({0, 0, upscaleH - 1, upscaleW - 1, 0, 0}).WithSize({upscaleW, upscaleH});
    newOp->SetKernel(kernel);
    ofmConn->quantization = Quantization::Unit();
    ofmConn->rounding = RoundMode::AUTO;
    *newOp->ConnectOutput(TensorUsage::OFM, ofmConn->tensor) = *ofmConn;
    result.emplace_back(std::move(newOp));
    return result;
}

std::vector<std::unique_ptr<SchedulerOperation>> DecomposeElementwise(Architecture *arch, std::unique_ptr<SchedulerOperation> op)
{
    std::vector<std::unique_ptr<SchedulerOperation>> result;
    auto ofmConn = op->Output(TensorUsage::OFM);
    auto &ofmShape = ofmConn->SliceShape();
    auto &ofmSlice = ofmConn->slice;
    auto ifmConn = op->Input(TensorUsage::IFM);
    auto &ifmShape = ifmConn->SliceShape();
    auto &ifmSlice = ifmConn->slice;

    ofmSlice.Initialize(ofmShape.WithZeros(), ofmShape);
    ifmSlice.Initialize(ifmShape.WithZeros(), ifmShape);
    if ( auto ifm2Conn = op->TryInput(TensorUsage::IFM1) )
    {
        auto &ifm2Shape = ifm2Conn->shape;
        auto &ifm2Slice = ifm2Conn->slice;

        ifm2Slice.Initialize(ifm2Shape.WithZeros(), ifm2Shape);
    }
    auto ofmRank = ofmShape.Size();
    if ( ofmRank > 3 && ofmShape.Elements() > ofmShape.Width() * ofmShape.Height() * ofmShape.Depth() )
    {
        return DecomposeLeadingDimensions(ofmRank - 3, arch, std::move(op), DecomposeElementwise);
    }
    if ( auto maxShape = Shape::Min(Shape(nullptr, ofmShape.Size(), MAX_DIM), ofmShape); maxShape != ofmShape )
    {
        return DecomposeBlocksElementwise(arch, std::move(op), maxShape, DecomposeElementwise);
    }
    result.emplace_back(std::move(op));
    return result;
}

std::vector<std::unique_ptr<SchedulerOperation>> DecomposeMatmul(Architecture *arch, std::unique_ptr<SchedulerOperation> op)
{
    std::vector<std::unique_ptr<SchedulerOperation>> result;
    auto ofmConn = op->Output(TensorUsage::OFM);
    auto &ofmShape = ofmConn->SliceShape();
    auto &ofmSlice = ofmConn->slice;
    auto ifmConn = op->Input(TensorUsage::IFM);
    auto &ifmShape = ifmConn->SliceShape();
    auto &ifmSlice = ifmConn->slice;

    ofmSlice.Initialize(ofmShape.WithZeros(), ofmShape);
    ifmSlice.Initialize(ifmShape.WithZeros(), ifmShape);

    // TODO MLBEDSW-9535: large tensor decomposition
    if ( auto ifm2Conn = op->TryInput(TensorUsage::IFM1) )
    {
        auto &ifm2Shape = ifm2Conn->shape;
        auto &ifm2Slice = ifm2Conn->slice;

        ifm2Slice.Initialize(ifm2Shape.WithZeros(), ifm2Shape);
    }

    auto ofmRank = ofmShape.Size();
    if ( ofmRank > 2 && (ofmShape.Elements() > ofmShape.Width() * ofmShape.Depth()) )
    {
        return DecomposeLeadingDimensions(ofmRank - 2, arch, std::move(op), DecomposeMatmul);
    }

    result.emplace_back(std::move(op));
    return result;
}

std::vector<std::unique_ptr<SchedulerOperation>> DecomposeReduce(Architecture *arch, std::unique_ptr<SchedulerOperation> op)
{
    std::vector<std::unique_ptr<SchedulerOperation>> result;
    auto ofmConn = op->Output(TensorUsage::OFM);
    auto ofmShape = ofmConn->SliceShape();
    auto &ofmSlice = ofmConn->slice;
    auto ifmConn = op->Input(TensorUsage::IFM);
    auto ifmShape = ifmConn->SliceShape();
    auto &ifmSlice = ifmConn->slice;

    ofmSlice.Initialize(ofmShape.WithZeros(), ofmShape);
    ifmSlice.Initialize(ifmShape.WithZeros(), ifmShape);

    const auto ifmRank = ifmShape.Size();
    auto attr = op->Attribute<axis_attr_t>();
    const int reducedAxis = attr->axis;
    assert(reducedAxis >= 0);
    assert(reducedAxis < ifmRank);
    const bool isReduceInH = reducedAxis == ifmRank - 3;
    const bool isReduceInW = reducedAxis == ifmRank - 2;
    const bool isReduceInC = reducedAxis == ifmRank - 1;

    // Decompose Reduce Min/Max/Sum with the following algorithm so that it can run on NPU.
    //
    // 1. Reshape the IFM/OFM so that the dimension to reduce is either H, W or C (depending on which type of operation
    //    it is) and IFM/OFM are 3D shapes. When reshaping >4D shapes, we may lose the slice information, so therefore,
    //    at this point slicing is not supported.
    // 2. Create operations so that the reduced axis is reduced in blocks of 64k, with a final operation to produce the
    //    results in the original OFM.

    // Figure out what we need to decompose
    ArchRequirements req{};
    auto qResult = OperatorQuery(arch, op.get(), &req);
    bool decomposeReshape = false;
    if ( qResult.Any(QueryResult::HasRequirements) && req.req.Any(ArchRequirement::Decompose) )
    {
        decomposeReshape = req.decomposeProps.Any(ArchProperty::ReduceAxis, ArchProperty::TensorDims);
    }

    // Reshape to a 3D tensor
    if ( decomposeReshape )
    {
        // Slice offset not supported if we need to reshape
        assert(ofmSlice.offset.GreaterMask(ofmSlice.offset.WithZeros()) == 0);
        assert(ifmSlice.offset.GreaterMask(ifmSlice.offset.WithZeros()) == 0);

        if ( op->Type() == OpType::ReduceSum )
        {
            // ReduceSum can only reduce in C
            assert(isReduceInC);

            // Reshape to 3D with all >=H dimensions in H
            ifmConn->shape = ReshapeTo3D(ifmConn->shape, {ifmConn->shape.Size() - 2, 1, 1});
            ifmSlice = {};
            ofmConn->shape = ReshapeTo3D(ofmConn->shape, {ofmConn->shape.Size() - 2, 1, 1});
            ofmSlice = {};
            attr->axis = 2;  // C
        }
        else
        {
            // Reshape to 3D around W
            ifmConn->shape = ReshapeTo3DAroundAxis(ifmConn->shape, reducedAxis);
            ifmSlice = {};
            ofmConn->shape = ReshapeTo3DAroundAxis(ofmConn->shape, reducedAxis);
            ofmSlice = {};
            op->SetKernel(op->Kernel()->WithSize({ifmConn->shape.Width() /* W */, 1 /* H */}));
            attr->axis = 1;  // W
        }

        return DecomposeReduce(arch, std::move(op));
    }

    // Handle reduced axis
    if ( ifmShape[reducedAxis] > MAX_DIM )
    {
        // Create an intermediate tensor
        const int blockCount = (ifmShape[reducedAxis] - 1) / MAX_DIM + 1;
        auto newTensor = ifmConn->tensor->Clone();
        newTensor->srcTensor = nullptr;
        newTensor->storageShape = ifmShape.With(reducedAxis, blockCount);

        LOG_TRACE1("DecomposeReduce: Reduce dimension too large, axis {}, size {}, intermediate shape ({})\n",
            reducedAxis, ifmShape[reducedAxis], newTensor->storageShape.ToString());

        for ( int blockIndex = 0; blockIndex < blockCount; blockIndex++ )
        {
            // Create one new reduce op for each block
            const int blockSize = std::min(MAX_DIM, ifmShape[reducedAxis] - blockIndex * MAX_DIM);
            std::unique_ptr<SchedulerOperation> subOp;
            Kernel kernel;
            if ( isReduceInH ) kernel = op->Kernel()->WithSize({1 /* W */, blockSize /* H */});
            else if ( isReduceInW ) kernel = op->Kernel()->WithSize({blockSize /* W */, 1 /* H */});
            subOp = MakeSubOperation(op.get(), isReduceInC ? nullptr : &kernel);

            auto *subOpIfmConn = subOp->IFM(0);
            subOpIfmConn->slice.offset = ifmSlice.offset.With(reducedAxis, blockIndex * MAX_DIM);
            subOpIfmConn->slice.shape = ifmSlice.shape.With(reducedAxis, blockSize);
            subOpIfmConn->quantization = ifmConn->quantization;
            auto *subOpOfmConn = subOp->OFM();
            subOpOfmConn->tensor = newTensor;
            subOpOfmConn->shape = newTensor->storageShape;
            subOpOfmConn->slice.offset = ofmSlice.offset.With(reducedAxis, blockIndex);
            subOpOfmConn->slice.shape = ofmSlice.shape.With(reducedAxis, 1);
            subOpOfmConn->quantization = ofmConn->quantization;
            newTensor->producers.push_back(subOp.get());

            LOG_TRACE1("DecomposeReduce: Block, IFM ({}) @ ({}) from ({}), OFM ({}) @ ({}) from ({})\n",
                subOpIfmConn->slice.shape.ToString(), subOpIfmConn->slice.offset.ToString(), subOpIfmConn->shape.ToString(),
                subOpOfmConn->slice.shape.ToString(), subOpOfmConn->slice.offset.ToString(), subOpOfmConn->shape.ToString());

            auto subOps = DecomposeReduce(arch, std::move(subOp));
            result.insert(result.end(), std::make_move_iterator(subOps.begin()), std::make_move_iterator(subOps.end()));
        }

        // Create one last reduce op that reduces all the blocks
        std::unique_ptr<SchedulerOperation> subOp;
        Kernel kernel;
        if ( isReduceInH ) kernel = op->Kernel()->WithSize({1 /* W */, blockCount /* H */});
        else if ( isReduceInW ) kernel = op->Kernel()->WithSize({blockCount /* W */, 1 /* H */});
        subOp = MakeSubOperation(op.get(), isReduceInC ? nullptr : &kernel);

        auto *subOpIfmConn = subOp->IFM(0);
        subOpIfmConn->tensor = newTensor;
        subOpIfmConn->shape = newTensor->storageShape;
        subOpIfmConn->slice.offset = newTensor->storageShape.WithZeros();
        subOpIfmConn->slice.shape = ifmSlice.shape.With(reducedAxis, blockCount);
        subOpIfmConn->quantization = Quantization::Unit();
        newTensor->consumers.push_back(subOp.get());
        auto *subOpOfmConn = subOp->OFM();
        subOpOfmConn->quantization = Quantization::Unit();

        LOG_TRACE1("DecomposeReduce: Final block, IFM ({}) @ ({}) from ({}), OFM ({}) @ ({}) from ({})\n",
            subOpIfmConn->slice.shape.ToString(), subOpIfmConn->slice.offset.ToString(), subOpIfmConn->shape.ToString(),
            subOpOfmConn->slice.shape.ToString(), subOpOfmConn->slice.offset.ToString(), subOpOfmConn->shape.ToString());

        auto subOps = DecomposeReduce(arch, std::move(subOp));
        result.insert(result.end(), std::make_move_iterator(subOps.begin()), std::make_move_iterator(subOps.end()));
        return result;
    }

    // Handle non-reduced axes
    for ( int axis = 0; axis < ifmRank; axis++ )
    {
        // At this point the reduced axis should not be too large
        assert(ifmShape[axis] <= MAX_DIM || axis != reducedAxis);

        if ( ifmShape[axis] > MAX_DIM )
        {
            return DecomposeLargeAxis(axis, MAX_DIM, arch, std::move(op), DecomposeReduce);
        }
    }

    result.emplace_back(std::move(op));
    return result;
}

std::vector<std::unique_ptr<SchedulerOperation>> DecomposeReverse(Architecture *arch, std::unique_ptr<SchedulerOperation> op)
{
    std::vector<std::unique_ptr<SchedulerOperation>> result;
    auto ofmConn = op->Output(TensorUsage::OFM);
    auto ofmShape = ofmConn->SliceShape();
    auto &ofmSlice = ofmConn->slice;
    auto ifmConn = op->Input(TensorUsage::IFM);
    auto ifmShape = ifmConn->SliceShape();
    auto &ifmSlice = ifmConn->slice;

    ofmSlice.Initialize(ofmShape.WithZeros(), ofmShape);
    ifmSlice.Initialize(ifmShape.WithZeros(), ifmShape);

    if ( auto ifm2Conn = op->TryInput(TensorUsage::IFM1) )
    {
        auto ifm2Shape = ifm2Conn->shape;
        auto &ifm2Slice = ifm2Conn->slice;

        ifm2Slice.Initialize(ifm2Shape.WithZeros(), ifm2Shape);
    }

    auto ofmRank = ofmShape.Size();
    auto attr = op->Attribute<axis_attr_t>();
    int reversedAxis = attr->axis;

    for ( int axis = 0; axis < ofmRank; axis++ )
    {
        if ( ofmShape[axis] > MAX_DIM )
        {
            auto subOps = DecomposeLargeAxis(axis, MAX_DIM, arch, std::move(op), DecomposeReverse);
            if ( axis == reversedAxis )
            {
                // For the reversed axis, we need to invert
                // the slice-offsets for the OFM.
                for ( auto &subOp : subOps )
                {
                    auto *subOfmConn = subOp->Output(TensorUsage::OFM);
                    subOfmConn->slice.offset[axis] = ofmShape[axis] - subOfmConn->slice.offset[axis] - subOfmConn->SliceShape()[axis];
                }
            }
            return subOps;
        }
    }

    result.emplace_back(std::move(op));
    return result;
}

// Swap two axes of a shape by adding one or more transpose ops to a scheduler connection
static std::vector<std::unique_ptr<SchedulerOperation>> SwapAxes(Architecture *arch, Shape &shape, SchedulerConnection *tail, int a, int b)
{
    std::vector<std::unique_ptr<SchedulerOperation>> result;

    assert(shape.IsValid());
    assert(tail);
    assert(a >= 0 && a < shape.Size());
    assert(b >= 0 && b < shape.Size());
    assert(a < b);

    LOG_TRACE2("SwapAxes: Swap ({}), {} <-> {}\n", shape.ToString(), a, b);

    // The hardware can perform all permutations of a 3D tensor. This means we can swap two arbitrary axes of a shape
    // with N axes like this:
    //
    // 1. Reshape to a 3D shape (0*1 ..., A, ... N-2*N-1) and swap axis 0 and 1 in the 3D shape. Now A is leftmost in
    //    the original shape.
    // 2. Reshape to a 3D shape (0*1 ..., B, ... N-2*N-1) and swap axis 1 and 2 in the 3D shape. Now B is rightmost in
    //    the original shape.
    // 3. Swap 0 and N-1.
    // 4. Swap back axis N-1 to position B, like in step 2.
    // 5. Swap back axis 0 to position A, like in step 1.

    // We can swap any two axes of the three innermost axes (H/W/C) of a shape if any of the following is true:
    //
    // A) The shape is 3D or less. I.e. the shape is (H, W, C) or (W, C).
    // B) The shape is 4D or more and all axes other than the three innermost axes (H/W/C) are ones. I.e. the shape
    //    is (1, H, W, C), (1, 1, H, W, C) or (1, 1, 1, H, W, C).
    if ( shape.Size() <= 3 || (a >= shape.Size() - 3 && b >= shape.Size() - 3 && shape.AxisProduct(0, -3) == 1) )
    {
        // Build transpose type for this swap
        Shape perm(nullptr, shape.Size());
        for ( int i = 0; i < shape.Size(); i++ )
            perm[i] = i;
        std::swap(perm[a], perm[b]);
        const auto transposeType = TransposeTypeFromShape(perm);

        const Shape &ifmShape = shape;
        const Shape ofmShape = ifmShape.Permute(uint32_t(transposeType));
        LOG_TRACE2("SwapAxes: Transpose ({}) -> ({}), 0x{:08x}\n", ifmShape.ToString(), ofmShape.ToString(), transposeType);

        // Create SchedulerOperation
        auto op = std::make_unique<SchedulerOperation>(OpType::Transpose);
        op->SetKernel(Kernel::UnitKernel());
        auto ifmConn = op->AddInput(TensorUsage::IFM);
        auto ofmConn = op->AddOutput(TensorUsage::OFM);

        // Create SchedulerTensor
        auto newTensor = std::make_shared<SchedulerTensor>();
        newTensor->format = tail->tensor->format;
        newTensor->memArea = tail->tensor->memArea;
        newTensor->storageShape = ofmShape;
        newTensor->bufferView = BufferView(nullptr, 0, DataTypeSizeBits(tail->tensor->dataType), ofmShape, Shape());
        newTensor->dataType = tail->tensor->dataType;
        newTensor->uid = GenerateUniqueId();

        // Connect input/output
        ifmConn->SetType(tail->Type());
        ifmConn->tensor = tail->tensor;
        ifmConn->tensor->consumers.push_back(op.get());
        ifmConn->shape = ifmShape;
        ofmConn->SetType(tail->Type());
        ofmConn->tensor = std::move(newTensor);
        ofmConn->tensor->producers.push_back(op.get());
        ofmConn->shape = ofmShape;
        ofmConn->transpose = transposeType;

        std::swap(shape[a], shape[b]);

        return DecomposeTranspose(arch, std::move(op));
    }

    if ( a == 0 && b == 1 )
    {
        // Swap of index 0 and 1 can always be done with 1 op
        LOG_TRACE2("SwapAxes: Left-anchored swap\n");
        auto tmp = ReshapeTo3D(shape, {1, 1, shape.Size() - 2});
        auto ops = SwapAxes(arch, tmp, tail, 0, 1);
        result.insert(result.end(), std::make_move_iterator(ops.begin()), std::make_move_iterator(ops.end()));
        std::swap(shape[a], shape[b]);
        LOG_TRACE2("SwapAxes: Current shape ({})\n", shape.ToString());

        return result;
    }

    if ( a == shape.Size() - 2 && b == shape.Size() - 1 )
    {
        // Swap of index N-2 and N-1 can always be done with 1 op
        LOG_TRACE2("SwapAxes: Right-anchored swap\n");
        auto tmp = ReshapeTo3D(shape, {shape.Size() - 2, 1, 1});
        auto ops = SwapAxes(arch, tmp, tail, 1, 2);
        result.insert(result.end(), std::make_move_iterator(ops.begin()), std::make_move_iterator(ops.end()));
        std::swap(shape[a], shape[b]);
        LOG_TRACE2("SwapAxes: Current shape ({})\n", shape.ToString());

        return result;
    }

    if ( a != 0 )
    {
        // Move A left
        LOG_TRACE2("SwapAxes: Move index {} ({}) leftmost\n", a, shape[a]);
        auto tmp1 = ReshapeTo3DAroundAxis(shape, a);
        auto ops1 = SwapAxes(arch, tmp1, tail, 0, 1);
        result.insert(result.end(), std::make_move_iterator(ops1.begin()), std::make_move_iterator(ops1.end()));
        shape = shape.Erase(a).Insert(0, shape[a]);
        LOG_TRACE2("SwapAxes: Current shape ({})\n", shape.ToString());

        // Swap (A is now leftmost)
        auto ops = SwapAxes(arch, shape, result.back()->OFM(), 0, b);
        result.insert(result.end(), std::make_move_iterator(ops.begin()), std::make_move_iterator(ops.end()));

        // Move A back to where it was
        LOG_TRACE2("SwapAxes: Move leftmost ({}) back to index {}\n", shape[0], a);
        auto tmp2 = ReshapeTo3D(shape, {1, a, shape.Size() - a - 1});
        auto ops2 = SwapAxes(arch, tmp2, result.back()->OFM(), 0, 1);
        result.insert(result.end(), std::make_move_iterator(ops2.begin()), std::make_move_iterator(ops2.end()));
        shape = shape.Erase(0).Insert(a, shape[0]);
        LOG_TRACE2("SwapAxes: Current shape ({})\n", shape.ToString());

        return result;
    }

    if ( b != shape.Size() - 1 )
    {
        // Move B right
        LOG_TRACE2("SwapAxes: Move index {} ({}) rightmost\n", b, shape[b]);
        auto tmp1 = ReshapeTo3DAroundAxis(shape, b);
        auto ops1 = SwapAxes(arch, tmp1, tail, 1, 2);
        result.insert(result.end(), std::make_move_iterator(ops1.begin()), std::make_move_iterator(ops1.end()));
        shape = shape.Erase(b).Insert(-1, shape[b]);
        LOG_TRACE2("SwapAxes: Current shape ({})\n", shape.ToString());

        // Swap (A is leftmost and B is rightmost)
        auto ops = SwapAxes(arch, shape, result.back()->OFM(), 0, shape.Size() - 1);
        result.insert(result.end(), std::make_move_iterator(ops.begin()), std::make_move_iterator(ops.end()));

        // Move B back to where it was
        LOG_TRACE2("SwapAxes: Move rightmost ({}) back to index {}\n", shape[-1], b);
        auto tmp2 = ReshapeTo3D(shape, {b, shape.Size() - b - 1, 1});
        auto ops2 = SwapAxes(arch, tmp2, result.back()->OFM(), 1, 2);
        result.insert(result.end(), std::make_move_iterator(ops2.begin()), std::make_move_iterator(ops2.end()));
        shape = shape.Erase(-1).Insert(b, shape[-1]);
        LOG_TRACE2("SwapAxes: Current shape ({})\n", shape.ToString());

        return result;
    }

    // Swap (A is leftmost and B is rightmost)
    assert(a == 0);
    assert(b == shape.Size() - 1);
    LOG_TRACE2("SwapAxes: Swap leftmost and rightmost\n");
    auto tmp = ReshapeTo3DAroundEdges(shape);
    auto ops = SwapAxes(arch, tmp, tail, 0, 2);
    result.insert(result.end(), std::make_move_iterator(ops.begin()), std::make_move_iterator(ops.end()));
    std::swap(shape[a], shape[b]);
    LOG_TRACE2("SwapAxes: Current shape ({})\n", shape.ToString());

    return result;
}

std::vector<std::unique_ptr<SchedulerOperation>> DecomposeTranspose(Architecture *arch, std::unique_ptr<SchedulerOperation> op)
{
    std::vector<std::unique_ptr<SchedulerOperation>> result;
    auto ifmConn = op->Input(TensorUsage::IFM);
    auto ofmConn = op->Output(TensorUsage::OFM);
    const auto &ifmShape = ifmConn->SliceShape();
    const auto axes = ifmShape.Size();

    ArchRequirements req{};
    auto qResult = OperatorQuery(arch, op.get(), &req);
    bool decomposeMask = false;
    bool decomposeAxes = false;
    bool decomposeLeadingDims = false;

    if ( qResult.Any(QueryResult::HasRequirements) && req.req.Any(ArchRequirement::Decompose) )
    {
        decomposeMask = req.decomposeProps.Any(ArchProperty::TransposeMask);
        decomposeAxes = req.decomposeProps.Any(ArchProperty::TensorAxis);
        decomposeLeadingDims = req.decomposeProps.Any(ArchProperty::TensorDims);
    }

    if ( decomposeMask || decomposeLeadingDims )
    {
        // Decompose unsupported transpose-masks or large IFM-dimensions
        // by unrolling the transpose-mask into many 3D-transpose operations.

        // We can handle TransposeType::None as an elementwise, because it's basically a memory copy
        if ( ofmConn->transpose == TransposeType::None )
        {
            LOG_TRACE1("DecomposeTranspose: Decomposing as elementwise\n");
            return DecomposeElementwise(arch, std::move(op));
        }

        assert(ifmConn->slice.offset.IsEmpty() && ifmConn->slice.shape.IsEmpty());
        assert(ofmConn->slice.offset.IsEmpty() && ofmConn->slice.shape.IsEmpty());

        // Decompose a transpose by peforming a selection sort of the axes. Each swap in the selection sort algorithm
        // expands to one or more transpose ops.
        //
        // Example:
        //
        // Input shape:        [ 3,  7, 11, 13]
        // Permutation vector: [ 1,  3,  0,  2]
        // Sort order:         [ 2,  0,  3,  1]
        // Output shape:       [ 7, 13,  3, 11]
        //
        // Selection sort swaps:
        //
        // Swap 1: Pos 0 <-> Pos 1: [7, 3,  11, 13]
        // Swap 2: Pos 1 <-> Pos 3: [7, 13, 11,  3]
        // Swap 3: Pos 2 <-> Pos 3: [7, 13,  3, 11]

        // Calculate sort order
        Shape order(nullptr, axes);
        uint32_t mask = uint32_t(ofmConn->transpose);
        for ( int i = axes - 1; i >= 0; i-- )
        {
            const int pos = axes - 1 - (mask & 0xF);
            order[pos] = i;
            mask = mask >> 4;
        }

        auto shape = ifmConn->shape;

        LOG_TRACE1("DecomposeTranspose: Sort order ({})\n", order.ToString());
        LOG_TRACE1("DecomposeTranspose: Initial shape ({})\n", shape.ToString());

        for ( int axis = 0; axis < axes; axis++ )
        {
            // Check if axis is already in the right place
            if ( order[axis] == axis ) continue;

            // Find where the axis is
            int i;
            for ( i = axis + 1; i < axes; i++ )
                if ( order[i] == axis ) break;
            assert(i < axes);

            // Move axis to right place
            LOG_TRACE1("DecomposeTranspose: Swap {} <-> {}\n", axis, i);
            auto tail = !result.empty() ? result.back()->OFM() : ifmConn;
            auto subOps = SwapAxes(arch, shape, tail, axis, i);
            result.insert(result.end(), std::make_move_iterator(subOps.begin()), std::make_move_iterator(subOps.end()));
            std::swap(order[axis], order[i]);
            LOG_TRACE1("DecomposeTranspose: Shape is now ({})\n", shape.ToString());
        }

        LOG_TRACE1("DecomposeTranspose: Final shape ({})\n", shape.ToString());

        assert(!result.empty());

        const auto &lastTensor = result.back()->OFM()->tensor;
        for ( auto &subOp : result )
        {
            auto ifm = subOp->IFM(0);
            auto ofm = subOp->OFM();
            if ( ofm->tensor == lastTensor )
            {
                // Adjust to that last output is written to the original OFM
                ofm->tensor = ofmConn->tensor;
                ofm->tensor->producers.push_back(subOp.get());
                ofm->SetType(ofmConn->Type());

                // Adjust so ops that write to original OFM has original quantization
                ifm->quantization = ifmConn->quantization;
                ofm->quantization = ofmConn->quantization;
            }
        }
        return result;
    }

    // We can handle all transpositions in a 3D shape
    if ( decomposeAxes )
    {
        for ( int axis = 0; axis < axes; axis++ )
        {
            if ( ifmShape[axis] > MAX_DIM )
            {
                // Initialize the shapes so that OFM slice is untransposed
                ofmConn->slice.Initialize(ifmShape.WithZeros(), ifmShape);
                ifmConn->slice.Initialize(ifmShape.WithZeros(), ifmShape);

                // OFM slice will be transposed by DecomposeLargeAxis
                LOG_TRACE1("DecomposeTranspose: Axis {} is too large ({})\n", axis, ifmShape[axis]);
                return DecomposeLargeAxis(axis, MAX_DIM, arch, std::move(op), DecomposeTranspose);
            }
        }
    }


    // No decomposition required
    result.push_back(std::move(op));
    return result;
}

std::vector<std::unique_ptr<SchedulerOperation>> DecomposeAvgPool(Architecture *arch, std::unique_ptr<SchedulerOperation> op)
{
    std::vector<std::unique_ptr<SchedulerOperation>> result;
    auto *ofmConn = op->Output(TensorUsage::OFM);
    auto *ifmConn = op->Input(TensorUsage::IFM);
    const auto &ofmShape = ofmConn->SliceShape();
    const auto &ifmShape = ifmConn->SliceShape();
    auto &ofmSlice = ofmConn->slice;
    auto &ifmSlice = ifmConn->slice;
    auto *kernel = op->Kernel();
    auto &padding = kernel->Padding();
    ofmSlice.Initialize(ofmShape.WithZeros(), ofmShape);
    ifmSlice.Initialize(ifmShape.WithZeros().WithHW(-padding.Top(), -padding.Left()), ifmShape);
    auto ofmRank = ofmShape.Size();
    if ( ofmRank > 3 && (ofmShape.Elements() > ofmShape.Height() * ofmShape.Width() * ofmShape.Depth()) )
    {
        return DecomposeLeadingDimensions(ofmRank - 3, arch, std::move(op), DecomposeAvgPool);
    }

    if ( !NeedsDecompose(arch, op.get()) )
    {
        UpdatePaddingAndIfmOffset(op.get());
        result.emplace_back(std::move(op));
        return result;
    }
    // Decomposition for large dimensions & strides is needed here.
    // If we get here, decomposition has failed, the resulting operations will be executed on CPU
    UpdatePaddingAndIfmOffset(op.get());
    result.emplace_back(std::move(op));
    return result;
}

std::vector<std::unique_ptr<SchedulerOperation>> DecomposeMaxPool(Architecture *arch, std::unique_ptr<SchedulerOperation> op)
{
    std::vector<std::unique_ptr<SchedulerOperation>> result;
    auto *ofmConn = op->Output(TensorUsage::OFM);
    auto *ifmConn = op->Input(TensorUsage::IFM);
    const auto &ofmShape = ofmConn->SliceShape();
    const auto &ifmShape = ifmConn->SliceShape();
    auto &ofmSlice = ofmConn->slice;
    auto &ifmSlice = ifmConn->slice;
    auto *kernel = op->Kernel();
    auto &padding = kernel->Padding();
    ofmSlice.Initialize(ofmShape.WithZeros(), ofmShape);
    ifmSlice.Initialize(ifmShape.WithZeros().WithHW(-padding.Top(), -padding.Left()), ifmShape);
    auto ofmRank = ofmShape.Size();
    if ( ofmRank > 3 && (ofmShape.Elements() > ofmShape.Height() * ofmShape.Width() * ofmShape.Depth()) )
    {
        return DecomposeLeadingDimensions(ofmRank - 3, arch, std::move(op), DecomposeMaxPool);
    }
    if ( !NeedsDecompose(arch, op.get()) )
    {
        UpdatePaddingAndIfmOffset(op.get());
        result.emplace_back(std::move(op));
        return result;
    }
    try
    {
        if ( auto newBlockShape = NewOfmBlockShape(arch, op.get()) )
        {
            return DecomposeBlocks(arch, std::move(op), newBlockShape, DecomposeMaxPool);
        }
    }
    catch ( const DecompositionFailure & )
    {
        UpdatePaddingAndIfmOffset(op.get());
        result.emplace_back(std::move(op));
        return result;
    }
    if ( arch->Constraints()->SupportsAccumulatorSaveRestore() && op->Kernel()->Stride().AreaXY() > 1 )
    {
        return DecomposeForStrides(arch, std::move(op), DecomposeMaxPool);
    }
    // If we get here, decomposition has failed, the resulting operations will be executed on CPU
    UpdatePaddingAndIfmOffset(op.get());
    result.emplace_back(std::move(op));
    return result;
}

std::vector<std::unique_ptr<SchedulerOperation>> DecomposeResize(Architecture *arch, std::unique_ptr<SchedulerOperation> op)
{
    std::vector<std::unique_ptr<SchedulerOperation>> result;
    auto ofmConn = op->Output(TensorUsage::OFM);
    auto &ofmShape = ofmConn->SliceShape();
    auto &ofmSlice = ofmConn->slice;
    auto ifmConn = op->Input(TensorUsage::IFM);
    auto &ifmShape = ifmConn->SliceShape();
    auto &ifmSlice = ifmConn->slice;

    ofmSlice.Initialize(ofmShape.WithZeros(), ofmShape);
    ifmSlice.Initialize(ifmShape.WithZeros(), ifmShape);

    ArchRequirements req{};
    auto qResult = OperatorQuery(arch, op.get(), &req);
    bool decomposeLeadingDims = false;
    if ( qResult.Any(QueryResult::HasRequirements) && req.req.Any(ArchRequirement::Decompose) )
    {
        decomposeLeadingDims = req.decomposeProps.Any(ArchProperty::TensorDims);
    }
    if ( decomposeLeadingDims )
    {
        return DecomposeLeadingDimensions(ofmShape.Size() - 3, arch, std::move(op), DecomposeResize);
    }
    result.emplace_back(std::move(op));
    return result;
}

}  // namespace regor
