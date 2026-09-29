from app.models import ComicPanel, ComicStory, PanelOutline


def build_comic_layout(
    outline: list[PanelOutline],
    story: ComicStory,
    image_urls: list[str],
) -> list[ComicPanel]:
    if not (len(outline) == len(story.panels) == len(image_urls)):
        raise ValueError("Outline, story and image counts must match.")

    story_map = {panel.panel_number: panel for panel in story.panels}

    if set(story_map) != {panel.panel_number for panel in outline}:
        raise ValueError("Panel numbers in outline and story do not match.")

    result: list[ComicPanel] = []

    for item, image_url in zip(outline, image_urls):
        panel_story = story_map[item.panel_number]
        result.append(
            ComicPanel(
                panel_number=item.panel_number,
                title=panel_story.title,
                image_url=image_url,
                image_prompt=item.image_prompt,
                scene_description=panel_story.scene_description,
                caption=panel_story.caption,
                narration=panel_story.narration,
            )
        )

    return result
