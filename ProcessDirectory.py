import sys

MIN_PYTHON = (3, 7)
assert sys.version_info >= MIN_PYTHON, f"requires Python {'.'.join([str(n) for n in MIN_PYTHON])} or newer"

from os import listdir, getcwd, system, replace, walk
from os.path import isfile, isdir, join
import re
from shutil import rmtree
from subprocess import Popen

cwd = getcwd()

inferenceScript = join(cwd, 'BackgroundMattingV2', 'inference_video.py')
modelPath = join('Models', 'PyTorch', 'pytorch_resnet50.pth')

if not isfile(inferenceScript):
    print(f'Inference script missing, expected to exist at \'{inferenceScript}\'')
    print('Check your working directory')
    sys.exit(1)

if not isfile(modelPath):
    print(f'Model missing, expected to exist at \'{modelPath}\'')
    print('Check your working directory')
    sys.exit(1)

if len(sys.argv) == 1:
    print("Specify input directory")
    sys.exit(1)

inputDir = sys.argv[1]

if not isdir(inputDir):
    print(f'{inputDir} is not a directory')

outputBase = join(inputDir, '__tmp')
if isdir(outputBase):
    print(f'Cleaning temporary output directory: {outputBase}')
    rmtree(outputBase)

for currentDir, dirnames, filenames in walk(inputDir):
    print (f'Processing directory: {currentDir}')

    for filename in filenames:
        fileMatch = re.match(r"(?P<base>.*)\.(?P<ext>mp4|mov|avi|mkv)$", filename)

        if fileMatch:
            base = fileMatch.group('base')
            ext = fileMatch.group('ext')
            print(f'Found video file {base}.{ext}')
            videoFile = join(currentDir, filename)
            bgFile = join(currentDir, f'{base}.png')
            outputMatteVideo = join(currentDir, f'{base}_matte.mp4')

            if not isfile(bgFile):
                print(f'Missing background image \'{bgFile}\', skipping this video!')
                continue

            if isfile(outputMatteVideo):
                print(f'Output file {outputMatteVideo} exists, skipping.')
                continue

            outputDir = join(outputBase, base)
            if isdir(outputDir):
                print(f'Cleaning temporary output directory: {outputDir}')
                rmtree(outputDir)

            print(f'Outputting to temporary dir: {outputDir}')
            print("Running inference script", flush=True)
            proc = Popen([
                'python', inferenceScript,
                '--model-type', 'mattingrefine',
                '--model-backbone', 'resnet50',
                '--model-checkpoint', modelPath,
                '--model-refine-mode', 'full',
                '--video-src', videoFile,
                '--video-bgr', bgFile,
                '--output-dir', outputDir,
                '--output-types', 'pha',
                '--output-format', 'video'])

            proc.wait()

            if proc.returncode != 0:
                print (f'Inference script failed with return code {proc.returncode}')

            tmpVideo = join(outputDir, 'pha.mp4')

            if isfile(tmpVideo):
                print (f'Copying output file from {tmpVideo} to {outputMatteVideo}')
                replace(tmpVideo, outputMatteVideo)

            if isdir(outputDir):
                print(f'Cleaning up temporary output directory: {outputDir}')
                rmtree(outputDir)

print("Done processing")
if isdir(outputBase):
    print(f'Cleaning temporary output directory: {outputBase}')
    rmtree(outputBase)
