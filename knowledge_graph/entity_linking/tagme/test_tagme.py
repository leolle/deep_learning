# -*- coding: utf-8 -*-
import tagme
import wikipedia
# Set the authorization token for subsequent calls.
tagme.GCUBE_TOKEN = "1e1a9d3f-47ab-4df1-a063-45301072978f-843339462"

TEXT = 'The man saw a Jaguar speed on the highway'
TEXT = 'Consumer protection legislation typically labels vehicles as "lemons" if the same problem recurs despite multiple repair attempts.'
# TEXT = 'Democrats not invited to DOJ briefing on FBI informant'
# TEXT = 'Zuckerberg avoided tough questions thanks to short EU testimony format'
TEXT = 'The prey saw the jaguar cross the jungle.'
text_annotations = tagme.annotate(TEXT)

# Print annotations with a score higher than 0.1
for ann in text_annotations.get_annotations(0.001):
    print(ann)
    print(wikipedia.summary(ann.entity_title)[:250] + '...')

# tomatoes_mentions = tagme.mentions(
#     "I definitely like ice cream better than tomatoes.")

# for mention in tomatoes_mentions.mentions:
#     print(mention)
