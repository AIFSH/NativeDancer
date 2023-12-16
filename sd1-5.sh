
apt -y install -qq aria2
# pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118
# pip install -q diffusers==0.21.4 transformers==4.32.0 accelerate==0.22.0 omegaconf==2.3.0 einops==0.6.1 av gradio

aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://hf-mirror.com/runwayml/stable-diffusion-v1-5/raw/main/model_index.json -d weights/pose_frame/stable-diffusion-v1-5 -o model_index.json
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://hf-mirror.com/runwayml/stable-diffusion-v1-5/resolve/main/vae/diffusion_pytorch_model.bin -d weights/pose_frame/stable-diffusion-v1-5/vae -o diffusion_pytorch_model.bin
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://hf-mirror.com/runwayml/stable-diffusion-v1-5/raw/main/vae/config.json -d weights/pose_frame/stable-diffusion-v1-5/vae -o config.json
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://hf-mirror.com/runwayml/stable-diffusion-v1-5/resolve/main/unet/diffusion_pytorch_model.bin -d weights/pose_frame/stable-diffusion-v1-5/unet -o diffusion_pytorch_model.bin
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://hf-mirror.com/runwayml/stable-diffusion-v1-5/raw/main/unet/config.json -d weights/pose_frame/stable-diffusion-v1-5/unet -o config.json
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://hf-mirror.com/runwayml/stable-diffusion-v1-5/raw/main/tokenizer/vocab.json -d weights/pose_frame/stable-diffusion-v1-5/tokenizer -o vocab.json
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://hf-mirror.com/runwayml/stable-diffusion-v1-5/raw/main/tokenizer/tokenizer_config.json -d weights/pose_frame/stable-diffusion-v1-5/tokenizer -o tokenizer_config.json
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://hf-mirror.com/runwayml/stable-diffusion-v1-5/raw/main/tokenizer/special_tokens_map.json -d weights/pose_frame/stable-diffusion-v1-5/tokenizer -o special_tokens_map.json
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://hf-mirror.com/runwayml/stable-diffusion-v1-5/raw/main/tokenizer/merges.txt -d weights/pose_frame/stable-diffusion-v1-5/tokenizer -o merges.txt
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://hf-mirror.com/runwayml/stable-diffusion-v1-5/resolve/main/text_encoder/pytorch_model.bin -d weights/pose_frame/stable-diffusion-v1-5/text_encoder -o pytorch_model.bin
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://hf-mirror.com/runwayml/stable-diffusion-v1-5/raw/main/text_encoder/config.json -d weights/pose_frame/stable-diffusion-v1-5/text_encoder -o config.json
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://hf-mirror.com/runwayml/stable-diffusion-v1-5/raw/main/scheduler/scheduler_config.json -d weights/pose_frame/stable-diffusion-v1-5/scheduler -o scheduler_config.json
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://hf-mirror.com/runwayml/stable-diffusion-v1-5/resolve/main/safety_checker/pytorch_model.bin -d weights/pose_frame/stable-diffusion-v1-5/safety_checker -o pytorch_model.bin
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://hf-mirror.com/runwayml/stable-diffusion-v1-5/raw/main/safety_checker/config.json -d weights/pose_frame/stable-diffusion-v1-5/safety_checker -o config.json
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://hf-mirror.com/runwayml/stable-diffusion-v1-5/raw/main/feature_extractor/preprocessor_config.json -d weights/pose_frame/stable-diffusion-v1-5/feature_extractor -o preprocessor_config.json