#
# Create: 2020/05/09
# Author: Cong Yang
# 
# Description: Python Implement of ITK ThresholdSegmentationLevelSetImageFilter
#              for uterus segementation.
#
# 
# Reference: ItkSoftwareGuide
# =============================================================================


import itk


inputFileName = 'p01_preMRI.nii'
outputFileName = 'Threshold_result.nii'
seedPoss = (
            (320, 240, 22), 
            (300, 230, 26)
            #(420, 340), 
            #(400, 420)
            )  # ((x1, y1, z1), (x2, y2, z2), ...)

initialDistance = float(5.0)
propagationScaling = float(10.0)

LowerT = 150    # not 0-255, but mri value
UpperT = 400

numberOfIterations = 1000
seedValue = -initialDistance

Dimension = 3

InputPixelType = itk.F
OutputPixelType = itk.UC

InputImageType = itk.Image[InputPixelType, Dimension]
OutputImageType = itk.Image[OutputPixelType, Dimension]

ReaderType = itk.ImageFileReader[InputImageType]
WriterType = itk.ImageFileWriter[OutputImageType]

reader = ReaderType.New()
reader.SetFileName(inputFileName)
inputImage = reader.GetOutput()
reader.Update()

FastMarchingFilterType = itk.FastMarchingImageFilter[
    InputImageType, InputImageType]
fastMarching = FastMarchingFilterType.New()

# Set seed
seeds = itk.VectorContainer[
    itk.UI, itk.LevelSetNode[InputPixelType, Dimension]].New()
seeds.Initialize()

for i, seedpos in enumerate(seedPoss):
    x, y, z = seedpos 
    seedPosition = itk.Index[Dimension]()
    seedPosition[0] = x
    seedPosition[1] = y
    seedPosition[2] = z

    node = itk.LevelSetNode[InputPixelType, Dimension]()
    node.SetValue(seedValue)
    node.SetIndex(seedPosition)

    seeds.InsertElement(i, node)

fastMarching.SetTrialPoints(seeds)
fastMarching.SetSpeedConstant(1.0)
fastMarching.SetOutputSize(
    inputImage.GetBufferedRegion().GetSize())

initalLV = fastMarching.GetOutput()
fastMarching.Update()

initalLV.SetSpacing(inputImage.GetSpacing())    # Must keep the same spacing with input dicom


ThresholdSegmentationFilterType = itk.ThresholdSegmentationLevelSetImageFilter[
    InputImageType, InputImageType, InputPixelType]
thresholdSeg = ThresholdSegmentationFilterType.New()
thresholdSeg.SetPropagationScaling(propagationScaling)
thresholdSeg.SetCurvatureScaling(1.0)
thresholdSeg.SetUpperThreshold(UpperT)
thresholdSeg.SetLowerThreshold(LowerT)
thresholdSeg.SetIsoSurfaceValue(0.0)
thresholdSeg.SetMaximumRMSError(0.02)
thresholdSeg.SetNumberOfIterations(numberOfIterations)
thresholdSeg.SetInput(initalLV)
thresholdSeg.SetFeatureImage(inputImage)


ThresholdingFilterType = itk.BinaryThresholdImageFilter[
    InputImageType, OutputImageType]
thresholder = ThresholdingFilterType.New()
thresholder.SetLowerThreshold(-1000.0)
thresholder.SetUpperThreshold(0.0)
thresholder.SetOutsideValue(itk.NumericTraits[OutputPixelType].min())
#thresholder.SetInsideValue(itk.NumericTraits[OutputPixelType].max())
thresholder.SetInsideValue(2)
thresholder.SetInput(thresholdSeg.GetOutput())



CastFilterType = itk.RescaleIntensityImageFilter[
    InputImageType, OutputImageType]

caster0 = CastFilterType.New()
caster4 = CastFilterType.New()

writer0 = WriterType.New()
writer4 = WriterType.New()

caster0.SetInput(inputImage)
writer0.SetInput(caster0.GetOutput())
writer0.SetFileName("Threshold_origin.nii")
caster0.SetOutputMinimum(itk.NumericTraits[OutputPixelType].min())
caster0.SetOutputMaximum(itk.NumericTraits[OutputPixelType].max())
writer0.Update()

caster4.SetInput(initalLV)
writer4.SetInput(caster4.GetOutput())
writer4.SetFileName("ThresholdOutput_fastMarch.nii")
caster4.SetOutputMinimum(itk.NumericTraits[OutputPixelType].min())
caster4.SetOutputMaximum(itk.NumericTraits[OutputPixelType].max())



writer = WriterType.New()
writer.SetFileName(outputFileName)
writer.SetInput(thresholder.GetOutput())
writer.Update()


print('\n================== Info ==================\n')
print('SeedPos: ', seedPoss)
print('Parameters: LowerThreshold={:0>3d}, UpperThreshold={:0>3d}'.format(LowerT, UpperT))
print(
    "Max. no. iterations: " +
    str(thresholdSeg.GetNumberOfIterations()) + "\n")
print(
    "Max. RMS error: " +
    str(thresholdSeg.GetMaximumRMSError()) + "\n")
print(
    "No. elpased iterations: " +
    str(thresholdSeg.GetElapsedIterations()) + "\n")
print("RMS change: " + str(thresholdSeg.GetRMSChange()) + "\n")

writer4.Update()
