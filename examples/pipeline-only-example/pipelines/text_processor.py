"""
Text Processing Pipeline - Pipeline-Only Example

This pipeline demonstrates lightweight text processing using only FlowerPower's
pipeline functionality without any job queue dependencies. It's perfect for
simple data processing tasks, quick analysis, and development workflows.
"""

import json
import logging
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from hamilton.function_modifiers import parameterize

from flowerpower.cfg import Config

logger = logging.getLogger(__name__)

# Load configuration parameters
BASE_DIR = Path(__file__).parent.parent
PARAMS = Config.load(str(BASE_DIR), {}).run.inputs


def raw_text_data(input_file: str, encoding: str) -> str:
    """Load raw text data from file."""
    file_path = BASE_DIR / input_file
    logger.info(f"Loading text data from {file_path}")

    with open(file_path, "r", encoding=encoding) as f:
        content = f.read()

    logger.info(f"Loaded {len(content)} characters of text data")
    return content


def text_chunks(raw_text_data: str, chunk_size: int) -> List[str]:
    """Split text into manageable chunks for processing."""
    chunks = []
    text = raw_text_data.strip()

    # Split by paragraphs first, then by chunk size if needed
    paragraphs = text.split("\n\n")
    current_chunk = ""

    for paragraph in paragraphs:
        if len(current_chunk + paragraph) <= chunk_size:
            current_chunk += paragraph + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n\n"

    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    logger.info(f"Split text into {len(chunks)} chunks")
    return chunks


def filtered_chunks(text_chunks: List[str], filters: Dict[str, Any]) -> List[str]:
    """Filter text chunks based on criteria."""
    min_words = filters.get("min_words", 0)
    max_words = filters.get("max_words", float("inf"))

    filtered = []
    for chunk in text_chunks:
        word_count = len(chunk.split())
        if min_words <= word_count <= max_words:
            filtered.append(chunk)
        else:
            logger.debug(f"Filtered out chunk with {word_count} words")

    logger.info(
        f"Filtered to {len(filtered)} chunks from {len(text_chunks)} original chunks"
    )
    return filtered


def word_statistics(
    filtered_chunks: List[str], operations: List[str], filters: Dict[str, Any]
) -> Dict[str, Any]:
    """Calculate word-level statistics for text chunks."""
    if "word_count" not in operations:
        return {}

    remove_stopwords = filters.get("remove_stopwords", False)

    # Common English stopwords
    stopwords = {
        "the",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "can",
        "a",
        "an",
        "this",
        "that",
        "these",
        "those",
        "i",
        "you",
        "he",
        "she",
        "it",
        "we",
        "they",
    }

    all_words = []
    chunk_stats = []

    for i, chunk in enumerate(filtered_chunks):
        # Extract words
        words = re.findall(r"\b[a-zA-Z]+\b", chunk.lower())

        if remove_stopwords:
            words = [w for w in words if w not in stopwords]

        all_words.extend(words)

        chunk_stats.append({
            "chunk_id": i,
            "word_count": len(words),
            "unique_words": len(set(words)),
            "most_common": Counter(words).most_common(5),
        })

    # Overall word statistics
    word_freq = Counter(all_words)

    statistics = {
        "total_words": len(all_words),
        "unique_words": len(word_freq),
        "most_common_words": word_freq.most_common(20),
        "chunk_statistics": chunk_stats,
        "vocabulary_richness": len(word_freq) / len(all_words) if all_words else 0,
    }

    logger.info(
        f"Calculated word statistics: {len(all_words)} total words, {len(word_freq)} unique"
    )
    return statistics


def sentence_statistics(
    filtered_chunks: List[str], operations: List[str]
) -> Dict[str, Any]:
    """Calculate sentence-level statistics for text chunks."""
    if "sentence_count" not in operations:
        return {}

    all_sentences = []
    chunk_stats = []

    for i, chunk in enumerate(filtered_chunks):
        # Simple sentence splitting
        sentences = re.split(r"[.!?]+", chunk)
        sentences = [s.strip() for s in sentences if s.strip()]

        all_sentences.extend(sentences)

        # Calculate sentence lengths
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_length = (
            sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        )

        chunk_stats.append({
            "chunk_id": i,
            "sentence_count": len(sentences),
            "avg_sentence_length": avg_length,
            "longest_sentence": max(sentence_lengths) if sentence_lengths else 0,
            "shortest_sentence": min(sentence_lengths) if sentence_lengths else 0,
        })

    # Overall sentence statistics
    all_lengths = [len(s.split()) for s in all_sentences]

    statistics = {
        "total_sentences": len(all_sentences),
        "avg_sentence_length": sum(all_lengths) / len(all_lengths)
        if all_lengths
        else 0,
        "longest_sentence_length": max(all_lengths) if all_lengths else 0,
        "shortest_sentence_length": min(all_lengths) if all_lengths else 0,
        "chunk_statistics": chunk_stats,
    }

    logger.info(f"Calculated sentence statistics: {len(all_sentences)} sentences")
    return statistics


def character_statistics(
    filtered_chunks: List[str], operations: List[str]
) -> Dict[str, Any]:
    """Calculate character-level statistics for text chunks."""
    if "character_count" not in operations:
        return {}

    all_text = " ".join(filtered_chunks)

    # Character frequency analysis
    char_freq = Counter(all_text.lower())

    # Remove spaces and punctuation for letter analysis
    letters_only = re.findall(r"[a-zA-Z]", all_text.lower())
    letter_freq = Counter(letters_only)

    chunk_stats = []
    for i, chunk in enumerate(filtered_chunks):
        chunk_stats.append({
            "chunk_id": i,
            "character_count": len(chunk),
            "letter_count": len(re.findall(r"[a-zA-Z]", chunk)),
            "digit_count": len(re.findall(r"[0-9]", chunk)),
            "punctuation_count": len(re.findall(r"[^\w\s]", chunk)),
        })

    statistics = {
        "total_characters": len(all_text),
        "total_letters": len(letters_only),
        "letter_frequency": letter_freq.most_common(),
        "most_common_characters": char_freq.most_common(20),
        "chunk_statistics": chunk_stats,
    }

    logger.info(f"Calculated character statistics: {len(all_text)} characters")
    return statistics


def keyword_analysis(
    filtered_chunks: List[str], operations: List[str]
) -> Dict[str, Any]:
    """Extract and analyze keywords from text chunks."""
    if "extract_keywords" not in operations:
        return {}

    # Simple keyword extraction based on frequency and length
    all_words = []
    chunk_keywords = []

    stopwords = {
        "the",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "can",
        "a",
        "an",
        "this",
        "that",
        "these",
        "those",
        "i",
        "you",
        "he",
        "she",
        "it",
        "we",
        "they",
    }

    for i, chunk in enumerate(filtered_chunks):
        # Extract meaningful words (3+ characters, not stopwords)
        words = re.findall(r"\b[a-zA-Z]{3,}\b", chunk.lower())
        keywords = [w for w in words if w not in stopwords]

        # Get most frequent keywords for this chunk
        word_freq = Counter(keywords)
        top_keywords = word_freq.most_common(10)

        all_words.extend(keywords)
        chunk_keywords.append({
            "chunk_id": i,
            "keywords": top_keywords,
            "keyword_count": len(set(keywords)),
        })

    # Global keyword analysis
    global_freq = Counter(all_words)

    analysis = {
        "global_keywords": global_freq.most_common(50),
        "total_unique_keywords": len(global_freq),
        "chunk_keywords": chunk_keywords,
        "keyword_density": len(set(all_words)) / len(all_words) if all_words else 0,
    }

    logger.info(f"Extracted {len(global_freq)} unique keywords")
    return analysis


def sentiment_analysis(
    filtered_chunks: List[str], operations: List[str]
) -> Dict[str, Any]:
    """Perform basic sentiment analysis on text chunks."""
    if "analyze_sentiment" not in operations:
        return {}

    # Simple sentiment word lists
    positive_words = [
        "good",
        "great",
        "excellent",
        "amazing",
        "wonderful",
        "fantastic",
        "positive",
        "success",
        "win",
        "best",
        "love",
        "like",
        "happy",
        "pleased",
        "satisfied",
        "brilliant",
        "outstanding",
        "superb",
        "magnificent",
        "perfect",
        "beautiful",
    ]

    negative_words = [
        "bad",
        "terrible",
        "awful",
        "horrible",
        "negative",
        "failure",
        "lose",
        "worst",
        "hate",
        "dislike",
        "sad",
        "angry",
        "disappointed",
        "frustrated",
        "ugly",
        "disgusting",
        "pathetic",
        "miserable",
        "dreadful",
        "appalling",
    ]

    chunk_sentiments = []
    overall_positive = 0
    overall_negative = 0

    for i, chunk in enumerate(filtered_chunks):
        chunk_lower = chunk.lower()

        pos_count = sum(1 for word in positive_words if word in chunk_lower)
        neg_count = sum(1 for word in negative_words if word in chunk_lower)

        # Determine sentiment
        if pos_count > neg_count:
            sentiment = "positive"
            confidence = min(0.9, 0.5 + (pos_count - neg_count) * 0.1)
        elif neg_count > pos_count:
            sentiment = "negative"
            confidence = min(0.9, 0.5 + (neg_count - pos_count) * 0.1)
        else:
            sentiment = "neutral"
            confidence = 0.5

        chunk_sentiments.append({
            "chunk_id": i,
            "sentiment": sentiment,
            "confidence": confidence,
            "positive_indicators": pos_count,
            "negative_indicators": neg_count,
        })

        overall_positive += pos_count
        overall_negative += neg_count

    # Overall sentiment
    if overall_positive > overall_negative:
        overall_sentiment = "positive"
    elif overall_negative > overall_positive:
        overall_sentiment = "negative"
    else:
        overall_sentiment = "neutral"

    analysis = {
        "overall_sentiment": overall_sentiment,
        "positive_indicators": overall_positive,
        "negative_indicators": overall_negative,
        "sentiment_score": (overall_positive - overall_negative)
        / max(1, overall_positive + overall_negative),
        "chunk_sentiments": chunk_sentiments,
    }

    logger.info(f"Completed sentiment analysis: {overall_sentiment} overall sentiment")
    return analysis


def text_analysis_results(
    filtered_chunks: List[str],
    word_statistics: Dict[str, Any],
    sentence_statistics: Dict[str, Any],
    character_statistics: Dict[str, Any],
    keyword_analysis: Dict[str, Any],
    sentiment_analysis: Dict[str, Any],
    process_timestamp: str,
    output_format: str,
    include_statistics: bool,
    save_to_file: bool,
) -> Dict[str, Any]:
    """Compile final text analysis results."""

    # Compile analysis results
    results = {
        "processing_metadata": {
            "timestamp": process_timestamp,
            "completed_at": datetime.now().isoformat(),
            "total_chunks_processed": len(filtered_chunks),
            "output_format": output_format,
        },
        "text_content": {
            "chunks": filtered_chunks,
            "total_chunks": len(filtered_chunks),
            "total_characters": sum(len(chunk) for chunk in filtered_chunks),
        },
    }

    # Add analysis results if they were computed
    if word_statistics:
        results["word_analysis"] = word_statistics

    if sentence_statistics:
        results["sentence_analysis"] = sentence_statistics

    if character_statistics:
        results["character_analysis"] = character_statistics

    if keyword_analysis:
        results["keyword_analysis"] = keyword_analysis

    if sentiment_analysis:
        results["sentiment_analysis"] = sentiment_analysis

    # Add processing statistics
    if include_statistics:
        results["processing_statistics"] = {
            "analysis_modules_used": [
                key
                for key in [
                    "word_analysis",
                    "sentence_analysis",
                    "character_analysis",
                    "keyword_analysis",
                    "sentiment_analysis",
                ]
                if key in results
            ],
            "processing_time": datetime.now().isoformat(),
            "success": True,
        }

    # Save to file if requested
    if save_to_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if output_format == "json":
            output_file = BASE_DIR / f"text_analysis_{timestamp}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            results["output_file"] = str(output_file)

        # Create symlink to latest
        latest_file = BASE_DIR / f"latest_text_analysis.{output_format}"
        if latest_file.exists():
            latest_file.unlink()
        latest_file.symlink_to(output_file.name)
        results["latest_file"] = str(latest_file)

    logger.info(f"Completed text analysis with {len(results) - 2} analysis modules")
    return results
