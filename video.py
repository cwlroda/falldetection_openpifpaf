"""Video demo application.

Use --scale=0.2 to reduce the input image size to 20%.
Use --json-output for headless processing.

Example commands:
    python3 -m pifpaf.video --source=0  # default webcam
    python3 -m pifpaf.video --source=1  # another webcam

    # streaming source
    python3 -m pifpaf.video --source=http://127.0.0.1:8080/video

    # file system source (any valid OpenCV source)
    python3 -m pifpaf.video --source=docs/coco/000000081988.jpg

Trouble shooting:
* MacOSX: try to prefix the command with "MPLBACKEND=MACOSX".
"""


import argparse
import json
import logging
import os
import sys
import time

import PIL
import torch
import torch.multiprocessing as mp

import cv2  # pylint: disable=import-error
from . import decoder, network, show, transforms, visualizer, __version__
from . import config, core, logger

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"
LOG = logging.getLogger(__name__)


class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter,
                      argparse.RawDescriptionHelpFormatter):
    pass


def cli():  # pylint: disable=too-many-statements,too-many-branches
    parser = argparse.ArgumentParser(
        prog='python3 -m openpifpaf.video',
        description=__doc__,
        formatter_class=CustomFormatter,
    )
    parser.add_argument('--version', action='version',
                        version='OpenPifPaf {version}'.format(version=__version__))

    network.cli(parser)
    decoder.cli(parser, force_complete_pose=False, instance_threshold=0.1, seed_threshold=0.5)
    show.cli(parser)
    visualizer.cli(parser)

    parser.add_argument('--source', default=None,
                        help='OpenCV source url. Integer for webcams. Supports rtmp streams.')
    parser.add_argument('--video-output', default=None, nargs='?', const=True,
                        help='video output file')
    parser.add_argument('--video-fps', default=show.AnimationFrame.video_fps, type=float)
    parser.add_argument('--show', default=False, action='store_true')
    parser.add_argument('--horizontal-flip', default=False, action='store_true')
    parser.add_argument('--no-colored-connections',
                        dest='colored_connections', default=True, action='store_false',
                        help='do not use colored connections to draw poses')
    parser.add_argument('--disable-cuda', action='store_true',
                        help='disable CUDA')
    parser.add_argument('--scale', default=1.0, type=float,
                        help='input image scale factor')
    parser.add_argument('--start-frame', type=int, default=0)
    parser.add_argument('--skip-frames', type=int, default=1)
    parser.add_argument('--max-frames', type=int)
    parser.add_argument('--json-output', default=None, nargs='?', const=True,
                        help='json output file')
    group = parser.add_argument_group('logging')
    group.add_argument('-q', '--quiet', default=False, action='store_true',
                       help='only show warning messages or above')
    group.add_argument('--debug', default=False, action='store_true',
                       help='print debug messages')
    args = parser.parse_args()

    args.debug_images = False

    # configure logging
    log_level = logging.INFO
    if args.quiet:
        log_level = logging.WARNING
    if args.debug:
        log_level = logging.DEBUG
    
    LOG = logger.Logger('openpifpaf').setup(log_level)

    network.configure(args)
    show.configure(args)
    visualizer.configure(args)
    show.AnimationFrame.video_fps = args.video_fps

    # check whether source should be an int
    if args.source is not None:
        args.source = int(args.source)

    # add args.device
    args.device = torch.device('cpu')
    if not args.disable_cuda and torch.cuda.is_available():
        args.device = torch.device('cuda')
    LOG.info('neural network device: %s', args.device)

    # standard filenames
    if args.video_output is True:
        args.video_output = os.path.dirname(__file__)+"/output/"+"output.mp4"
        if os.path.exists(args.video_output):
            os.remove(args.video_output)
    assert args.video_output is None or not os.path.exists(args.video_output)
    if args.json_output is True:
        args.json_output = '{}_output.json'.format(args.source)
        if os.path.exists(args.json_output):
            os.remove(args.json_output)
    assert args.json_output is None or not os.path.exists(args.json_output)

    return args


def processor_factory(args):
    model, _ = network.factory_from_args(args)
    model = model.to(torch.device("cpu"))
    processor = decoder.factory_from_args(args, model)
    return processor, model


def inference(stream, animation, processor, model, annotation_painter):
    (RTSPURL, ID, scale) = stream
    capture = cv2.VideoCapture(RTSPURL, cv2.CAP_FFMPEG)
    
    if capture.isOpened():
        LOG.info('Loaded stream: ' + RTSPURL)
    else:
        LOG.error('Cannot open stream: ' + RTSPURL)


    last_loop = time.time()
    
    for frame_i, (ax, ax_second) in enumerate(animation.iter()):
        _, image = capture.read()
        input_fps = capture.get(cv2.CAP_PROP_FPS)
        
        if image is None:
            LOG.info('no more images captured')
            break
        
        if float(scale) != 1.0:
            image = cv2.resize(image, None, fx=float(scale), fy=float(scale))
            LOG.debug('resized image size: %s', image.shape)
        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        if ax is None:
            ax, ax_second = animation.frame_init(image)
        visualizer.BaseVisualizer.image(image)
        visualizer.BaseVisualizer.common_ax = ax_second

        start = time.time()
        image_pil = PIL.Image.fromarray(image)
        processed_image, _, __ = transforms.EVAL_TRANSFORM(image_pil, [], None)
        LOG.debug('preprocessing time %.3fs', time.time() - start)

        preds = processor.batch(model, torch.unsqueeze(processed_image, 0), device=torch.device("cpu"))[0]

        ax.imshow(image)
        annotation_painter.annotations(ax, preds, ID, input_fps)

        LOG.info('frame %d, loop time = %.3fs, input FPS = %.3f, output FPS = %.3f',
                frame_i,
                time.time() - last_loop,
                input_fps,
                1.0 / (time.time() - last_loop))
        last_loop = time.time()


def main():
    args = cli()
    processor, model = processor_factory(args)

    # create keypoint painter
    keypoint_painter = show.KeypointPainter(color_connections=args.colored_connections, linewidth=6)
    annotation_painter = show.AnnotationPainter(keypoint_painter=keypoint_painter)

    if args.source is None:
        settings = config.ConfigParser().getConfig()
        streams = core.MultiStreamLoader(settings['RTSPAPI'])
    else:
        stream = (args.source, "webcam", args.scale)

    animation = show.AnimationFrame(
        show=args.show,
        video_output=args.video_output,
        second_visual=args.debug or args.debug_indices,
    )

    processes = []
    
    for stream in streams.generateStreams():
        process = mp.Process(target=inference, args=(stream, animation, processor, model, annotation_painter))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()


if __name__ == '__main__':
    main()

