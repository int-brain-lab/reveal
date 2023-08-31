
import os
os.system("export PYTHONPATH='/Users/chris/Documents/PYTHON/int-brain-lab/ibldevtools/olivier/modules'")
import reveal
from pathlib import Path

REVEAL_PATH = Path.home().joinpath('Documents/JS/reveal.js')
IMG_PATH = Path.home().joinpath('Documents/PYTHON/int-brain-lab/ibldevtools/chris/spikesorting')
RES_PATH = IMG_PATH.joinpath('residuals')
VENN_PATH = IMG_PATH.joinpath('spikevenns')
NOTFOUND_IMG = RES_PATH / "notfound.png"

prez = reveal.Presentation(name="Residuals", path_reveal=REVEAL_PATH)

pids = [
    "11a5a93e-58a9-4ed0-995e-52279ec16b98",
    "16ad5eef-3fa6-4c75-9296-29bf40c5cfaa",
    "1a276285-8b0e-4cc9-9f0a-a3a002978724",
    "1e104bf4-7a24-4624-a5b2-c2c8289c0de7",
    "5d570bf6-a4c6-4bf1-a14b-2c878c84ef0e",
    "5f7766ce-8e2e-410c-9195-6bf089fea4fd",
    "6638cfb3-3831-4fc2-9327-194b76cf22e1",
    "749cb2b7-e57e-4453-a794-f6230e4d0226",
    "d7ec0892-0a6c-4f4f-9d8f-72083692af5c",
    "da8dfec1-d265-44e8-84ce-6ae9c109b8bd",
    "dab512bd-a02d-4c1f-8dbc-9155a163efc0",
    "dc7e9403-19f7-409f-9240-05ee57cb7aea",
    "e8f9fba4-d151-4b00-bee7-447f0f3e752c",
    "eebcaf65-7fa4-4118-869d-a084e84530e2",
    "fe380793-8035-414e-b000-09bfe5ece92a",
]

sorters = ["NEW_WT", "PYKS", "RERUN"]
sorter_names = {"PYKS": "PyKS old whitening", "NEW_WT": "PyKS", "RERUN": "PyKS Low Thresh", "KS4": "KS4", "DART": "dartsort"}

for pid in pids:
    prez.new_section()
    # for s in sorters:
    #     if s == "KS4":
    #         car_img = RES_PATH / f"CAR_{s}_{pid}.png"
    #         whitened_img = RES_PATH / f"WHITENED_{s}_{pid}.png"
    #         prez.add_slide_compare(full_path_image1=car_img,
    #                                full_path_image2=whitened_img,
    #                                title=f"{pid}: {sorter_names[s]} CAR vs Whitened")
    #     else:
    #         destriped_img = RES_PATH / f"DESTRIPED_{s}_{pid}.png"
    #         res_img = RES_PATH / f"RES_{s}_{pid}.png"
    #         model_img = RES_PATH / f"MODEL_{s}_{pid}.png"
    #         whitened_img = RES_PATH / f"WHITENED_{s}_{pid}.png"
    #         butter_img = RES_PATH / f"BUTTER_{s}_{pid}.png"
    #         butter_whitened_img = RES_PATH / f"WHITENED_BUTTER_{s}_{pid}.png"

    #         prez.add_slide_compare(full_path_image1=destriped_img,
    #                             full_path_image2=res_img,
    #                             title=f"{pid}: {sorter_names[s]} Destriped vs Residual")
    #         prez.add_slide_compare(full_path_image1=destriped_img,
    #                             full_path_image2=model_img,
    #                             title=f"{pid}: {sorter_names[s]} Destriped vs Templates")
    #         prez.add_slide_compare(full_path_image1=destriped_img,
    #                             full_path_image2=whitened_img,
    #                             title=f"{pid}: {sorter_names[s]} Destriped vs Whitened")
            # i don't think we want this actually
            # prez.add_slide_compare(full_path_image1=butter_img,
            #                     full_path_image2=butter_whitened_img,
            #                     title=f"{pid}: {sorter_names[s]} Butter vs Whitened")
    for s in sorters:
        destriped_img = RES_PATH / f"DESTRIPED_{s}_{pid}.png"
        res_img = RES_PATH / f"RES_{s}_{pid}.png"
        prez.add_slide_compare(full_path_image1=destriped_img,
                                full_path_image2=res_img,
                                title=f"{pid}:\n {sorter_names[s]} Destriped vs Residual")
    for s in sorters:
        destriped_img = RES_PATH / f"DESTRIPED_{s}_{pid}.png"
        model_img = RES_PATH / f"MODEL_{s}_{pid}.png"
        prez.add_slide_compare(full_path_image1=destriped_img,
                                full_path_image2=model_img,
                                title=f"{pid}:\n {sorter_names[s]} Destriped vs Templates")
    for s in sorters:
        destriped_img = RES_PATH / f"DESTRIPED_{s}_{pid}.png"
        whitened_img = RES_PATH / f"WHITENED_{s}_{pid}.png"
        prez.add_slide_compare(full_path_image1=destriped_img,
                                full_path_image2=whitened_img,
                                title=f"{pid}:\n {sorter_names[s]} Destriped vs Whitened")
    # KS4 
    car_img = RES_PATH / f"CAR_KS4_{pid}.png"
    whitened_img = RES_PATH / f"WHITENED_KS4_{pid}.png"
    prez.add_slide_compare(full_path_image1=car_img,
                        full_path_image2=whitened_img,
                        title=f"{pid}:\n KS4 CAR vs Whitened")
    # Dart
    dart_img = RES_PATH / f"DESTRIPED_DART_{pid}.png"
    prez.add_slide_compare(full_path_image1=dart_img,
                           full_path_image2=dart_img,
                         title=f"{pid}: Dart Destriped")
    # Spike venn diagrams
    spikevenn_img = VENN_PATH / f"{pid}_venn.png"
    prez.add_slide_image(full_path_image=spikevenn_img,
                         title=f"{pid}: Spike venn diagram")
    # Dredge
    dredge_img = RES_PATH / f"DREDGE_{pid}.png"
    if not dredge_img.exists():
        dredge_img = NOTFOUND_IMG
    prez.add_slide_image(full_path_image=dredge_img,
                         title="Dredge plot")
    prez.close_section()

prez.build()

os.system(f"aws s3 cp {REVEAL_PATH}/Residuals.html s3://reveal.internationalbrainlab.org/Residuals.html ")
os.system(f"aws s3 sync {REVEAL_PATH}/images/Residuals/ s3://reveal.internationalbrainlab.org/images/Residuals/")