def mock_video_description():
    # This function returns a mock description of what might be happening in the video.
    return (
        "00:00 Security camera shows a white van approaching a soldier at a border checkpoint.\n"
        "00:01 White van approaches soldier standing on the sidewalk at a border security checkpoint.\n"
        "00:02 White van veers onto the sidewalk, nearing the soldier at the security checkpoint.\n"
        "00:03 White van strikes soldier, throwing him onto the hood near the security checkpoint.\n"
        "00:04 White van halts near a soldier, who is injured and attempting to recover.\n"
        "00:05 Van driver exits vehicle, approaching injured soldier who is on the ground at checkpoint.\n"
        "00:06 Attacker engages in physical confrontation with the injured soldier near the white van.\n"
        "00:07 Attacker grapples with the soldier near the white van.\n"
        "00:08 Attacker physically assaults the soldier, forcing him backward.\n"
        "Final Summery: A white van at a border checkpoint suddenly veers onto the sidewalk, striking a soldier and throwing him to the ground. The driver exits the vehicle and physically assaults the injured soldier, forcing him backward. The violent confrontation unfolds rapidly near the van, capturing the alarming sequence on the security camera.\n"
    )

def mock_chat_analyze():
    return [
        """ I’ve found instances of this vehicle with the same license plate 🚐.
        For example, it was at the border on October 5, 2024, at 7:22 AM.""",

        """This car appeared at the border gate three times in the past month.
        ⚠️ On two occasions, it was parked near the border without crossing. 
        The third instance is the video you provided, which is linked to the terror attack.
        🚨 It seems the driver was gathering intelligence on the border patrol before committing the crime.""",

        """Sure. Here are the links for the videos: 
        - October 2, 2024, at 7:49 AM 
        - October 5, 2024, at 7:22 AM 
        - October 6, 2024, at 8:31 AM""",


    ]

"""
Could you check for this white van in the previous records?
Please search all the border cameras for the appearance of this car and provide me with a summary of its movements.
Can you provide me with links to each video so I can review them myself?
"""