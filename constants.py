MODELS = list( {
        "Taiyi-Chinese-v0.1": "IDEA-CCNL/Taiyi-Stable-Diffusion-1B-Chinese-v0.1",
        "Taiyi-Chinese-Anime-v0.1": "IDEA-CCNL/Taiyi-Stable-Diffusion-1B-Anime-Chinese-v0.1",
        "Chinese-style-sd-2-v0.1":"Midu/chinese-style-stable-diffusion-2-v0.1",
        "Stable-Diffusion-2.1": "stabilityai/stable-diffusion-2-1",
        "OpenJourney": "prompthero/openjourney",
        "Anything-v3-better-vae":  "Linaqruf/anything-v3-better-vae"
    }.keys())

SCHEDULERS = [
    "PNDM", 
    "LMS",
    "DDIM",
    "Euler",
    "Euler_A",
    "DPMSolver",
    "Heun",
    "KDPM2_A"
]