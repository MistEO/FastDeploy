import fastdeploy as fd
import cv2
import os


def parse_arguments():
    import argparse
    import ast
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model", required=True, help="Path of PP-ShiTuV2 detector model.")
    parser.add_argument(
        "--image", type=str, required=True, help="Path of test image file.")
    parser.add_argument(
        "--device",
        type=str,
        default='cpu',
        help="Type of inference device, support 'cpu' or 'gpu' or 'ipu' or 'kunlunxin' or 'ascend' ."
    )
    parser.add_argument(
        "--device_id",
        type=int,
        default=0,
        help="Define which GPU card used to run model.")
    parser.add_argument(
        "--backend",
        type=str,
        default="default",
        help="Type of inference backend, support ort/trt/paddle/openvino, default 'openvino' for cpu, 'tensorrt' for gpu"
    )
    return parser.parse_args()


def build_option(args):

    option = fd.RuntimeOption()

    if args.device.lower() == "gpu":
        option.use_cuda(args.device_id)

    if args.backend.lower() == "trt":
        assert args.device.lower(
        ) == "gpu", "TensorRT backend require inference on device GPU."
        option.use_trt_backend()

    elif args.backend.lower() == "pptrt":
        assert args.device.lower(
        ) == "gpu", "Paddle-TensorRT backend require inference on device GPU."
        option.use_paddle_infer_backend()
        option.paddle_infer_option.enable_trt = True
        option.paddle_infer_option.collect_trt_shape = True
        option.trt_option.set_shape("image", [1, 3, 640, 640],
                                    [1, 3, 640, 640], [1, 3, 640, 640])
        option.trt_option.set_shape("scale_factor", [1, 2], [1, 2], [1, 2])
        option.trt_option.set_shape("im_shape", [1, 2], [1, 2], [1, 2])

    elif args.backend.lower() == "ort":
        option.use_ort_backend()

    elif args.backend.lower() == "paddle":
        option.use_paddle_infer_backend()

    elif args.backend.lower() == "openvino":
        assert args.device.lower(
        ) == "cpu", "OpenVINO backend require inference on device CPU."
        option.use_openvino_backend()

    elif args.backend.lower() == "pplite":
        assert args.device.lower(
        ) == "cpu", "Paddle Lite backend require inference on device CPU."
        option.use_lite_backend()

    return option


args = parse_arguments()

# 配置runtime，加载模型
runtime_option = build_option(args)

model_file = os.path.join(args.model, "inference.pdmodel")
params_file = os.path.join(args.model, "inference.pdiparams")
config_file = os.path.join(args.model, "infer_cfg.yml")
model = fd.vision.classification.PPShiTuV2Detector(
    model_file, params_file, config_file, runtime_option=runtime_option)

# 预测主体检测结果
im = cv2.imread(args.image)
result = model.predict(im)

# 预测结果可视化
vis_im = fd.vision.vis_detection(im, result, score_threshold=0.5)
cv2.imwrite("visualized_result.jpg", vis_im)
print("Visualized result save in ./visualized_result.jpg")

print(result)
