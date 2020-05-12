import itk


inputFileName = 'p01_sag.jpg'
outputFileName = 'result.nii'
seedPosX = 300
seedPosY = 330
#seedPosZ = 20

initialDistance = float(5.0)
#propagationScaling = float(10.0)
numberOfIterations = 1000
seedValue = -initialDistance

# Canny Edge level set parameters =====================
cannyThreshold = 7.
cannyVariance = 0.1
advectionScaling = 10.
isoSurfaceValue = 127.5
# ======================================================

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
#inputImage.SetSpacing((1., 1., 1.))
print('spacing', inputImage.GetSpacing())

DiffusionFilterType = itk.GradientAnisotropicDiffusionImageFilter[
    InputImageType, InputImageType]
diffusion = DiffusionFilterType.New()
diffusion.SetNumberOfIterations(5)
diffusion.SetTimeStep(0.125)
diffusion.SetConductanceParameter(1.0)
diffusion.SetInput(reader.GetOutput())


FastMarchingFilterType = itk.FastMarchingImageFilter[
    InputImageType, InputImageType]
fastMarching = FastMarchingFilterType.New()


CannySegmentationLevelSetImageFilterType = itk.CannySegmentationLevelSetImageFilter[
    InputImageType, InputImageType, InputPixelType]
cannySegmentation = CannySegmentationLevelSetImageFilterType.New()
cannySegmentation.SetAdvectionScaling(advectionScaling)
cannySegmentation.SetCurvatureScaling(1.0)
cannySegmentation.SetPropagationScaling(0.0)
cannySegmentation.SetMaximumRMSError(0.01)
cannySegmentation.SetNumberOfIterations(numberOfIterations)
cannySegmentation.SetThreshold(cannyThreshold)
cannySegmentation.SetVariance(cannyVariance)
cannySegmentation.SetIsoSurfaceValue(isoSurfaceValue)
cannySegmentation.SetInput(diffusion.GetOutput())        # ???
cannySegmentation.SetFeatureImage(fastMarching.GetOutput())    # ???


ThresholdingFilterType = itk.BinaryThresholdImageFilter[
    InputImageType, OutputImageType]
thresholder = ThresholdingFilterType.New()
thresholder.SetLowerThreshold(-1000.0)
thresholder.SetUpperThreshold(0.0)
thresholder.SetOutsideValue(itk.NumericTraits[OutputPixelType].min())
#thresholder.SetInsideValue(itk.NumericTraits[OutputPixelType].max())
thresholder.SetInsideValue(2)
thresholder.SetInput(cannySegmentation.GetOutput())

seedPosition = itk.Index[Dimension]()
seedPosition[0] = seedPosX
seedPosition[1] = seedPosY
#seedPosition[2] = seedPosZ

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
caster3 = CastFilterType.New()
caster4 = CastFilterType.New()

writer0 = WriterType.New()
writer3 = WriterType.New()
writer4 = WriterType.New()

caster0.SetInput(reader.GetOutput())
writer0.SetInput(caster0.GetOutput())
writer0.SetFileName("origin.nii")
caster0.SetOutputMinimum(itk.NumericTraits[OutputPixelType].min())
caster0.SetOutputMaximum(itk.NumericTraits[OutputPixelType].max())
writer0.Update()

caster3.SetInput(diffusion.GetOutput())
writer3.SetInput(caster3.GetOutput())
writer3.SetFileName("CannyOutput_diffusion.nii")
caster3.SetOutputMinimum(itk.NumericTraits[OutputPixelType].min())
caster3.SetOutputMaximum(itk.NumericTraits[OutputPixelType].max())
writer3.Update()

caster4.SetInput(fastMarching.GetOutput())
writer4.SetInput(caster4.GetOutput())
writer4.SetFileName("CannyOutput_fastMarch.nii")
caster4.SetOutputMinimum(itk.NumericTraits[OutputPixelType].min())
caster4.SetOutputMaximum(itk.NumericTraits[OutputPixelType].max())
writer4.Update()

fastMarching.SetOutputSize(
    reader.GetOutput().GetBufferedRegion().GetSize())

writer = WriterType.New()
writer.SetFileName(outputFileName)
writer.SetInput(thresholder.GetOutput())
writer.Update()

'''
# Write speed image
cannySegmentation.GenerateSpeedImage()  # Generate speed image to fun tune the parameters

SpeedImageType = CannySegmentationLevelSetImageFilterType.SpeedImageType
SpeedWriterType = itk.ImageFileWriter[SpeedImageType]
speedWriter = SpeedWriterType.New()
speedWriter.SetFileName('CannyOutput_speedImage.nii')
speedWriter.SetInput(cannySegmentation.GetSpeedImage())
speedWriter.Update()
'''
print(
    "Max. no. iterations: " +
    str(cannySegmentation.GetNumberOfIterations()) + "\n")
print(
    "Max. RMS error: " +
    str(cannySegmentation.GetMaximumRMSError()) + "\n")
print(
    "No. elpased iterations: " +
    str(cannySegmentation.GetElapsedIterations()) + "\n")
print("RMS change: " + str(cannySegmentation.GetRMSChange()) + "\n")

