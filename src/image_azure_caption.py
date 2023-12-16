import json
import os
import azure.ai.vision as sdk

# Load credentials from a JSON file (config.json)
with open("config.json", "r") as config_file:
    config = json.load(config_file)

vision_key = config["VISION_KEY"]
vision_endpoint = config["VISION_ENDPOINT"]

service_options = sdk.VisionServiceOptions(vision_endpoint, vision_key)

def process_image_caption(image_path):
    vision_source = sdk.VisionSource(filename=image_path)
    analysis_options = sdk.ImageAnalysisOptions()
    analysis_options.features = (
        sdk.ImageAnalysisFeature.CAPTION |
        sdk.ImageAnalysisFeature.TEXT
    )
    analysis_options.language = "en"
    analysis_options.gender_neutral_caption = True
    image_analyzer = sdk.ImageAnalyzer(service_options, vision_source, analysis_options)
    result = image_analyzer.analyze()
    if result.reason == sdk.ImageAnalysisResultReason.ANALYZED:
        output_sentences = []
        if result.caption is not None:
            caption_sentence = "Caption: '{}', Confidence {:.4f}".format(result.caption.content, result.caption.confidence)
            output_sentences.append(caption_sentence)
        if result.text is not None:
            text_sentence = "Identified Text:"
            for line in result.text.lines:
                text_sentence += " " + line.content
            output_sentences.append(text_sentence)
        return "\n".join(output_sentences) if output_sentences else "No caption or text identified in the image."
    else:
        error_details = sdk.ImageAnalysisErrorDetails.from_result(result)
        return f"Analysis failed. Error reason: {error_details.reason}, Error code: {error_details.error_code}, Error message: {error_details.message}"