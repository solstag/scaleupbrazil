scaleupbrazil/captricity
========================

This directory has scripts related to using Captricity to convert scanned survey forms 
into datasets for analysis. 

There are several different sub-projects; broadly, the first few of these encompass
getting Captricity to turn scanned survey forms into an electronic dataset:

* upload scanned survey forms to our server
* prepare uploaded survey by rotating, resizing, converting to jpg
* route each survey through the Captricity API, using different templates based
  on our survey's skip patterns (to save money)
* download the resulting datasets

Once we have an electronic dataset from Captricity, we compare it to the results from
the hand-entered dataset. This will yield a list of questionnaires and items where
the two sources differ. In order to resolve these differences, we need

* an adjudication app which presents a third person with each disputed item to get a
  third entry
* a final decision app which will let members of the study team personally decide
  what value results from cases where all three sources (captricity, manual entry,
  and the adjudicator)
  
Finally, as a background to all of these tasks, there are some tools which will be used
to track each questionnaire's progress through this process.

We're in the process of moving more detailed documentation to the wiki (TODO LINK).







