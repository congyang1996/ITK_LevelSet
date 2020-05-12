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


inputFileName = 'p01_trans2.jpg'
outputFileName = 'Threshold_result.nii'
seedPosX = 360
seedPosY = 280


initialDistance = float(5.0)
propagationScaling = float(10.0)

LowerT = 100
UpperT = 250

numberOfIterations = 1000
seedValue = -initialDistance

Dimension = 2

InputPixelType = itk.F
OutputPixelType = itk.UC

InputImageType = itk.Image[InputPixelType, Dimension]
OutputImageType = itk.Image[OutputPixelType, Dimension]

ReaderType = itk.ImageFileReader[InputImageType]
WriterType = itk.ImageFileWriter[OutputImageType]

reader = ReaderType.New()
reader.SetFileName(inputFileName)
inputImage = reader.GetOutput()

FastMarchingFilterType = itk.FastMarchingImageFilter[
    InputImageType, InputImageType]
fastMarching = FastMarchingFilterType.New()

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
thresholdSeg.SetInput(fastMarching.GetOutput())
thresholdSeg.SetFeatureImage(reader.GetOutput())


ThresholdingFilterType = itk.BinaryThresholdImageFilter[
    InputImageType, OutputImageType]
thresholder = ThresholdingFilterType.New()
thresholder.SetLowerThreshold(-1000.0)
thresholder.SetUpperThreshold(0.0)
thresholder.SetOutsideValue(itk.NumericTraits[OutputPixelType].min())
#thresholder.SetInsideValue(itk.NumericTraits[OutputPixelType].max())
thresholder.SetInsideValue(2)
thresholder.SetInput(thresholdSeg.GetOutput())

seedPosition = itk.Index[Dimension]()
seedPosition[0] = seedPosX
seedPosition[1] = seedPosY


node = itk.LevelSetNode[InputPixelType, Dimension]()
node.SetValue(seedValue)
node.SetIndex(seedPosition)

seeds = itk.VectorContainer[
    itk.UI, itk.LevelSetNode[InputPixelType, Dimension]].New()
seeds.Initialize()
seeds.InsertElement(0, node)

fastMarching.SetTrialPoints(seeds)
fastMarching.SetSpeedConstant(1.0)

CastFilterType = itk.RescaleIntensityImageFilter[
    InputImageType, OutputImageType]

caster0 = CastFilterType.New()
caster4 = CastFilterType.New()

writer0 = WriterType.New()
writer4 = WriterType.New()

caster0.SetInput(reader.GetOutput())
writer0.SetInput(caster0.GetOutput())
writer0.SetFileName("Threshold_origin.nii")
caster0.SetOutputMinimum(itk.NumericTraits[OutputPixelType].min())
caster0.SetOutputMaximum(itk.NumericTraits[OutputPixelType].max())
writer0.Update()

caster4.SetInput(fastMarching.GetOutput())
writer4.SetInput(caster4.GetOutput())
writer4.SetFileName("ThresholdOutput_fastMarch.nii")
caster4.SetOutputMinimum(itk.NumericTraits[OutputPixelType].min())
caster4.SetOutputMaximum(itk.NumericTraits[OutputPixelType].max())

fastMarching.SetOutputSize(
    reader.GetOutput().GetBufferedRegion().GetSize())

writer = WriterType.New()
writer.SetFileName(outputFileName)
writer.SetInput(thresholder.GetOutput())
writer.Update()


print('\n================== Info ==================\n')
print('SeedPos: x={:0>3d}, y={:0>3d}'.format(seedPosX, seedPosY))
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
