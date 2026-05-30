from understanding.claim_classifier import (
    classify_claim
)

claims = [

    "Nagaland University hosted Startup Sprint on 22 April",

    "5 people were killed in a road accident in Kohima",

    "Prime Minister announced a new scheme",

    "The Earth revolves around the Sun",

    "Hornbill Festival was held in Nagaland",

    "Nagaland government launched a new policy",

    "20 students were injured in a bus accident"
]

for claim in claims:

    result = classify_claim(
        claim
    )

    print("\n" + "=" * 50)

    print("CLAIM:")
    print(claim)

    print("\nCLASSIFICATION:")

    print(
        result
    )
