import os
import re
import nltk
from nltk.tokenize import sent_tokenize
from groq import Groq

# Download NLTK data at the beginning
print("Setting up NLTK resources...")
try:
    nltk.download("punkt", quiet=True)
    # Also download punkt_tab explicitly if needed
    nltk.download("punkt_tab", quiet=True)
except Exception as e:
    print(f"NLTK download warning: {e}")


def summarize_video(video_info, verbose=True):
    """
    Takes video information and returns a structured summarized version

    Args:
        video_info (dict): Dictionary containing video information
        verbose (bool): Whether to print status messages

    Returns:
        str: A structured, formatted summary of the video content
    """
    # Get transcript from video_info
    transcript = video_info.get("transcript", "")
    title = video_info.get("title", "Unknown Video")
    description = video_info.get("description", "")

    # If no transcript, use description or return a message
    if not transcript or transcript == "Transcript unavailable":
        if description:
            content = description
        else:
            return "No transcript or description available for summarization."
    else:
        content = transcript

    # Use Groq if API key is available, otherwise fall back to basic summarization
    groq_key = os.getenv("GROQ_API_KEY")

    if not groq_key:
        if verbose:
            print("Warning: Groq API key not found. Using basic summarization.")
    elif len(content) <= 100:
        if verbose:
            print("Warning: Content too short for AI summarization.")
    else:
        if verbose:
            print("Using Groq for summarization...")

    if groq_key and len(content) > 100:
        return groq_structured_summary(title, content, groq_key)
    else:
        return basic_structured_summary(title, content)


def groq_structured_summary(title, content, api_key):
    """Generate a structured summary using Groq"""
    try:
        client = Groq(api_key=api_key)

        # Clean transcript - more aggressive cleaning
        cleaned_content = re.sub(
            r"\b(um|uh|like|you know|so|basically|actually|right|okay|yeah|just|kind of|sort of)\b",
            "",
            content,
        )
        # Remove timestamps if they exist in format [00:00]
        cleaned_content = re.sub(r"\[\d{1,2}:\d{2}\]", "", cleaned_content)
        # Remove speaker labels if they exist
        cleaned_content = re.sub(r"\b[A-Z][a-z]*\s*\:", "", cleaned_content)
        # Normalize whitespace
        cleaned_content = re.sub(r"\s+", " ", cleaned_content).strip()

        # More aggressive truncation to stay under token limits
        max_length = 5000  # Significantly reduced from 25000 to stay under token limits
        if len(cleaned_content) > max_length:
            cleaned_content = cleaned_content[:max_length] + "..."

        prompt = f"""Analyze and summarize this YouTube video transcript about "{title}":
        
{cleaned_content}

Generate a DETAILED and SPECIFIC summary with concrete information from the transcript, using Notion-compatible Markdown:

1. Start with a comprehensive paragraph that captures the main topics, speakers, and purpose

2. Create a section titled "## Highlights" with 5-7 emoji bullet points with SPECIFIC information, not generic placeholders
   Format as "- 🔍 **Topic:** Specific detail from the transcript"

3. Create a section titled "## Key Insights" with 5-7 detailed points that analyze specific content from the video
   Format as "- 💡 **Concept:** Detailed explanation with specific examples"

4. End with a conclusion paragraph that synthesizes the main value of this content

All bullet points must contain ACTUAL DETAILS from the transcript, not generic placeholders.
Use specific names, numbers, techniques or concepts mentioned.
Use simple Notion-compatible Markdown - headers with ## format, bullet points with -, bold with **.
"""

        # Try with 70B model first, fallback to 8B model if rate limited
        try:
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional content analyzer who extracts specific details and insights from transcripts. Format your response using Notion-compatible Markdown only.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=1500,
            )
        except Exception as e:
            if "rate_limit" in str(e).lower():
                print("Rate limit hit with 70B model, falling back to 8B model")
                response = client.chat.completions.create(
                    model="llama3-8b-8192",  # Fallback to smaller model
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional content analyzer who extracts specific details and insights from transcripts. Format your response using Notion-compatible Markdown only.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.5,
                    max_tokens=1500,
                )
            else:
                raise e

        summary = response.choices[0].message.content
        return summary
    except Exception as e:
        print(f"Groq summarization error: {e}")
        # Fall back to basic summarization
        return basic_structured_summary(title, content)


def basic_structured_summary(title, content):
    """Generate a structured summary using basic text extraction"""
    try:
        # Clean the content
        clean_content = re.sub(r"\s+", " ", content).strip()

        # Basic summarization: extract first few sentences
        sentences = sent_tokenize(clean_content)

        # Take first 3-5 sentences, or fewer if not available
        num_sentences = min(5, len(sentences))
        basic_summary = " ".join(sentences[:num_sentences])

        if len(basic_summary) > 500:
            basic_summary = basic_summary[:500] + "..."

        # Create a structured summary with Notion-compatible formatting
        structured_summary = f"""
{basic_summary}

## Highlights

- 🎯 **Main Topic:** {title}

- 🔑 **Key Points:** Important details from the video

- 💡 **Notable Insight:** A significant concept from the content

## Key Insights

- 🌟 **{title.split()[0] if title != 'Unknown Video' else 'Content'} Overview:** The video discusses important concepts related to this topic.

- 🔍 **Detailed Analysis:** Further exploration of the main ideas presented.

- ⚙️ **Technical Aspects:** Important technical details mentioned in the video.

This video provides valuable information about {title}. The main takeaways center around the key points discussed throughout the presentation.
"""
        return structured_summary.strip()
    except Exception as e:
        print(f"Basic summarization error: {e}")
        return f"Failed to generate a structured summary. Error: {e}"


def summarize_playlist(playlist_videos):
    """
    Summarizes multiple videos in a playlist.

    Args:
        playlist_videos (list): A list of dictionaries, each containing video details.

    Returns:
        list: A list of summaries for each video.
    """
    summaries = []
    for video in playlist_videos:
        summary = summarize_video(video)
        summaries.append(summary)
