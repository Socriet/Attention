# Analysis

## Layer 2, Head 1

This attention head appears to have learned to pay attention to the token that immediately precedes each token. For almost every token in the sequence, the brightest cell in its row corresponds to the previous token's column, establishing a backward-looking local context across the sequence.

Example Sentences:
- The [MASK] jumped over the lazy dog.
- We walked across the [MASK] before sunset.

## Layer 4, Head 2

This attention head appears to pay attention to the relationship between adjectives and the nouns they modify. In particular, adjective tokens attend strongly to the subsequent noun tokens that they describe, helping the model associate descriptive properties with the appropriate entity.

Example Sentences:
- The bright [MASK] illuminated the dark alley.
- She wore an elegant blue [MASK] to the dinner.