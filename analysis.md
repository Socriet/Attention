# Analysis

## Layer 2, Head 5

This attention head appears to pay attention to the previous token. Each
token attends mostly to the token immediately before it, which shows up as a
bright diagonal just below the main diagonal of the diagram. The first token,
[CLS], has no previous token and attends to itself, and [SEP] attends to
[CLS], so the pattern has small exceptions at the edges of the sentence.

Example Sentences:
- his [MASK] was unbelievable.
- The quick brown fox jumped over the lazy [MASK].

## Layer 3, Head 10

This attention head appears to pay attention to the next token. Each token
attends almost entirely to the token immediately after it, which shows up as
a bright diagonal just above the main diagonal. This is a very clean pattern:
for example, "his" attends to [MASK], and "was" attends to "unbelievable". The
last token, [SEP], attends back to [CLS].

Example Sentences:
- his [MASK] was unbelievable.
- The quick brown fox jumped over the lazy [MASK].