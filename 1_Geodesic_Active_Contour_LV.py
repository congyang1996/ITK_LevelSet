#
# Create: 2020/05/09
# Author: Cong Yang
# 
# Description: Python Implement of ITK GeodesicActiveContourLevelSetImageFilter
#              for uterus segementation.
#
# Modified from https://itk.org/ITKExamples/src/Segmentation/LevelSets/SegmentWithGeodesicActiveContourLevelSet/Documentation.html
# Reference: ItkSoftwareGuide
# =============================================================================

import sys  # restore
import itk


inputFileName = 'p01_sag.jpg'
outputFileName = 'GAC_result.nii'
seedPosX = 300
seedPosY = 330

initialDistance = float(5.0)
sigma = float(1.0)
alpha = float(-0.7)
beta = float(3.0)
propagationScaling = float(10.0)
numberOfIterations = 1000
seedValue = -initialDistance

Dimension = 2

InputPixelType = itk.F
OutputPixelType = itk.UC

InputImageType = itk.Image[InputPixelType, Dimension]
OutputImageType = itk.Image[OutputPixelType, Dimension]

ReaderType = itk.ImageFileReader[InputImageType]
WriterType = itk.ImageFileWriter[OutputImageType]

# Reader
reader = ReaderType.New()
reader.SetFileName(inputFileName)
inputImage = reader.GetOutput()
#inputImage.SetSpacing((1., 1., 1.))


# CurvatureAnisotropicDiffusionImageFilter
SmoothingFilterType = itk.CurvatureAnisotropicDiffusionImageFilter[
    InputImageType, InputImageType]
smoothing = SmoothingFilterType.New()
smoothing.SetTimeStep(0.125)
smoothing.SetNumberOfIterations(5)
smoothing.SetConductanceParameter(9.0)
smoothing.SetInput(inputImage)


# GradientMagnitudeRecursiveGaussianImageFilter
GradientFilterType = itk.GradientMagnitudeRecursiveGaussianImageFilter[
    InputImageType, InputImageType]
gradientMagnitude = GradientFilterType.New()
gradientMagnitude.SetSigma(sigma)
gradientMagnitude.SetInput(smoothing.GetOutput())


# SigmoidImageFilter
SigmoidFilterType = itk.SigmoidImageFilter[InputImageType, InputImageType]
sigmoid = SigmoidFilterType.New()
sigmoid.SetOutputMinimum(0.0)
sigmoid.SetOutputMaximum(1.0)
sigmoid.SetAlpha(alpha)
sigmoid.SetBeta(beta)
sigmoid.SetInput(gradientMagnitude.GetOutput())


# FastMarchingImageFilter
FastMarchingFilterType = itk.FastMarchingImageFilter[
    InputImageType, InputImageType]
fastMarching = FastMarchingFilterType.New()


# GeodesicActiveContourLevelSetImageFilter
GeoActiveContourFilterType = itk.GeodesicActiveContourLevelSetImageFilter[
    InputImageType, InputImageType, InputPixelType]
geodesicActiveContour = GeoActiveContourFilterType.New()
geodesicActiveContour.SetPropagationScaling(propagationScaling)
geodesicActiveContour.SetCurvatureScaling(1.0)
geodesicActiveContour.SetAdvectionScaling(1.0)
geodesicActiveContour.SetMaximumRMSError(0.02)
geodesicActiveContour.SetNumberOfIterations(numberOfIterations)
geodesicActiveContour.SetInput(fastMarching.GetOutput())
geodesicActiveContour.SetFeatureImage(sigmoid.GetOutput())


# BinaryThresholdImageFilter
ThresholdingFilterType = itk.BinaryThresholdImageFilter[
    InputImageType, OutputImageType]
thresholder = ThresholdingFilterType.New()
thresholder.SetLowerThreshold(-1000.0)
thresholder.SetUpperThreshold(0.0)
thresholder.SetOutsideValue(itk.NumericTraits[OutputPixelType].min())
#thresholder.SetInsideValue(itk.NumericTraits[OutputPixelType].max())
thresholder.SetInsideValue(2)   # Use value 2 to show green label in ITK-Snap software
thresholder.SetInput(geodesicActiveContour.GetOutput())


# Set seed
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


# Cast to unsigned char and write output
CastFilterType = itk.RescaleIntensityImageFilter[
    InputImageType, OutputImageType]

caster0 = CastFilterType.New()
caster1 = CastFilterType.New()
caster2 = CastFilterType.New()
caster3 = CastFilterType.New()
caster4 = CastFilterType.New()

writer0 = WriterType.New()
writer1 = WriterType.New()
writer2 = WriterType.New()
writer3 = WriterType.New()
writer4 = WriterType.New()

caster0.SetInput(reader.GetOutput())
writer0.SetInput(caster0.GetOutput())
writer0.SetFileName("GAC_origin.nii")
caster0.SetOutputMinimum(itk.NumericTraits[OutputPixelType].min())
caster0.SetOutputMaximum(itk.NumericTraits[OutputPixelType].max())
writer0.Update()

caster1.SetInput(smoothing.GetOutput())
writer1.SetInput(caster1.GetOutput())
writer1.SetFileName("GACOutput_smooth.nii")
caster1.SetOutputMinimum(itk.NumericTraits[OutputPixelType].min())
caster1.SetOutputMaximum(itk.NumericTraits[OutputPixelType].max())
writer1.Update()

caster2.SetInput(gradientMagnitude.GetOutput())
writer2.SetInput(caster2.GetOutput())
writer2.SetFileName("GACOutput_grad.nii")
caster2.SetOutputMinimum(itk.NumericTraits[OutputPixelType].min())
caster2.SetOutputMaximum(itk.NumericTraits[OutputPixelType].max())
writer2.Update()

caster3.SetInput(sigmoid.GetOutput())
writer3.SetInput(caster3.GetOutput())
writer3.SetFileName("GACOutput_sigmoid.nii")
caster3.SetOutputMinimum(itk.NumericTraits[OutputPixelType].min())
caster3.SetOutputMaximum(itk.NumericTraits[OutputPixelType].max())
writer3.Update()

caster4.SetInput(fastMarching.GetOutput())
writer4.SetInput(caster4.GetOutput())
writer4.SetFileName("GACOutput_fastMarch.nii")
caster4.SetOutputMinimum(itk.NumericTraits[OutputPixelType].min())
caster4.SetOutputMaximum(itk.NumericTraits[OutputPixelType].max())

fastMarching.SetOutputSize(
    reader.GetOutput().GetBufferedRegion().GetSize())

writer4.Update()

writer = WriterType.New()
writer.SetFileName(outputFileName)
writer.SetInput(thresholder.GetOutput())
writer.Update()


print('\n================== Info ==================\n')
print('SeedPos: x={:0>3d}, y={:0>3d}'.format(seedPosX, seedPosY))
print('Parameters: alpha={:.2f}, beta={:.2f}, propagationScaling={:.2f}'.format(alpha, beta, propagationScaling))

print(
    "Max. no. iterations: " +
    str(geodesicActiveContour.GetNumberOfIterations()))
print(
    "Max. RMS error: " +
    str(geodesicActiveContour.GetMaximumRMSError()))
print(
    "No. elpased iterations: " +
    str(geodesicActiveContour.GetElapsedIterations()))
print("RMS change: " + str(geodesicActiveContour.GetRMSChange()))



