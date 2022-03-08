from d2r_image.processing_data import UI_ROI
from d2r_image.data_models import ScreenObject


# class TownNpcScreenObjects:
#     Malah = ScreenObject(
#         refs=["MALAH_45", "MALAH_BACK", "MALAH_FRONT", "MALAH_SIDE_2", "MALAH_SIDE"],
#         threshold=0.38,
#         best_match=True,
#         use_grayscale=False
#     )


class MainMenuScreenObjects:
    PlayBtn=ScreenObject(
        refs=["PLAY_BTN", "PLAY_BTN_GRAY"],
        roi=UI_ROI.playButton,
        threshold=0.9,
        best_match=True,
        use_grayscale=True,
    )
    Normal=ScreenObject(
        refs=["NORMAL_BTN"],
        roi=UI_ROI.difficultySelect,
        threshold=0.9,
        use_grayscale=True
    )
    Nightmare=ScreenObject(
        refs=["NIGHTMARE_BTN"],
        roi=UI_ROI.difficultySelect,
        threshold=0.9,
        use_grayscale=True
    )
    Hell=ScreenObject(
        refs=["HELL_BTN"],
        roi=UI_ROI.difficultySelect,
        threshold=0.9,
        use_grayscale=True
    )
    Online=ScreenObject(
        refs=["ONLINE"],
        roi=UI_ROI.offlineOnline,
        threshold=0.9,
        use_grayscale=True
    )
    Offline=ScreenObject(
        refs=["OFFLINE"],
        roi=UI_ROI.offlineOnline,
        threshold=0.9,
        use_grayscale=True
    )


class LoadingScreenObjects:
    Loading=ScreenObject(
        refs=["LOADING"],
        roi=UI_ROI.difficultySelect,
        threshold=0.9,
        use_grayscale=True
    )
    ExitingGame=ScreenObject(
        refs=["EXITING_GAME"],
        roi=UI_ROI.exitGameLogo,
        threshold=0.9,
        use_grayscale=True
    )
