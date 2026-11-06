import os
import sys
import logging
from datetime import datetime
from pathlib import Path

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import tensorflow as tf
from PIL import Image, ImageDraw, ImageFont
from transformers import AutoTokenizer, TFBertForMaskedLM

tf.get_logger().setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)

MODEL = "bert-base-uncased"

K = 3

BASE_DIR = Path(__file__).resolve().parent
FONT_PATH = BASE_DIR / "assets" / "fonts" / "OpenSans-Regular.ttf"

if FONT_PATH.exists():
    FONT = ImageFont.truetype(str(FONT_PATH), 28)
else:
    FONT = ImageFont.load_default()

GRID_SIZE = 40
PIXELS_PER_WORD = 200


def main():
    text = input("Text: ")

    # Tokenize input
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    inputs = tokenizer(text, return_tensors="tf")
    mask_token_index = get_mask_token_index(tokenizer.mask_token_id, inputs)
    if mask_token_index is None:
        sys.exit(f"Input must include mask token {tokenizer.mask_token}.")

    # Use model to process input
    model = TFBertForMaskedLM.from_pretrained(MODEL)
    result = model(**inputs, output_attentions=True)

    # Generate predictions
    mask_token_logits = result.logits[0, mask_token_index]
    top_tokens = tf.math.top_k(mask_token_logits, K).indices.numpy()
    for token in top_tokens:
        print(text.replace(tokenizer.mask_token, tokenizer.decode([token])))

    # Visualize attentions
    visualize_attentions(inputs.tokens(), result.attentions)


def get_mask_token_index(mask_token_id, inputs):
    """
    Return the index of the token with the specified `mask_token_id`, or
    `None` if not present in the `inputs`.
    """
    input_ids = inputs["input_ids"][0].numpy().tolist()
    try:
        return input_ids.index(mask_token_id)
    except ValueError:
        return None


def get_color_for_attention_score(attention_score):
    """
    Return a tuple of three integers representing a shade of gray for the
    given `attention_score`. Each value should be in the range [0, 255].
    """
    score = float(attention_score)
    val = round(score * 255)
    val = max(0, min(255, int(val)))
    return (val, val, val)


def visualize_attentions(tokens, attentions):
    """
    Produce a graphical representation of self-attention scores.

    For each attention layer, one diagram should be generated for each
    attention head in the layer. Each diagram should include the list of
    `tokens` in the sentence. The filename for each diagram should
    include both the layer number (starting count from 1) and head number
    (starting count from 1).
    """
    # Create subfolder 
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = BASE_DIR / "outputs" / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Saving attention diagrams to: {output_dir}")

    for i, layer_attentions in enumerate(attentions):
        layer_number = i + 1
        num_heads = len(layer_attentions[0])
        for k in range(num_heads):
            head_number = k + 1
            generate_diagram(
                layer_number,
                head_number,
                tokens,
                layer_attentions[0][k],
                output_dir=output_dir
            )


def generate_diagram(layer_number, head_number, tokens, attention_weights, output_dir=None):
    """
    Generate a diagram representing the self-attention scores for a single
    attention head. The diagram shows one row and column for each of the
    `tokens`, and cells are shaded based on `attention_weights`, with lighter
    cells corresponding to higher attention scores.

    The diagram is saved with a filename that includes both the `layer_number`
    and `head_number`.
    """
    if output_dir is None:
        output_dir = BASE_DIR

    # Create new image
    image_size = GRID_SIZE * len(tokens) + PIXELS_PER_WORD
    img = Image.new("RGBA", (image_size, image_size), "black")
    draw = ImageDraw.Draw(img)

    # Draw each token onto the image
    for i, token in enumerate(tokens):
        token_image = Image.new("RGBA", (image_size, image_size), (0, 0, 0, 0))
        token_draw = ImageDraw.Draw(token_image)
        token_draw.text(
            (image_size - PIXELS_PER_WORD, PIXELS_PER_WORD + i * GRID_SIZE),
            token,
            fill="white",
            font=FONT
        )
        token_image = token_image.rotate(90)
        img.paste(token_image, mask=token_image)

        _, _, width, _ = draw.textbbox((0, 0), token, font=FONT)
        draw.text(
            (PIXELS_PER_WORD - width, PIXELS_PER_WORD + i * GRID_SIZE),
            token,
            fill="white",
            font=FONT
        )

    for i in range(len(tokens)):
        y = PIXELS_PER_WORD + i * GRID_SIZE
        for j in range(len(tokens)):
            x = PIXELS_PER_WORD + j * GRID_SIZE
            color = get_color_for_attention_score(attention_weights[i][j])
            draw.rectangle((x, y, x + GRID_SIZE, y + GRID_SIZE), fill=color)

    # Save image
    save_path = Path(output_dir) / f"Attention_Layer{layer_number}_Head{head_number}.png"
    img.save(save_path)


if __name__ == "__main__":
    main()