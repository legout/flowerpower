# FlowerPower pipeline hello_world_parallel.py
# Created on 2025-10-14 02:39:22

####################################################################################################
# Import necessary libraries
# NOTE: Remove or comment out imports that are not used in the pipeline

from hamilton.function_modifiers import parameterize, dataloader, datasaver
from hamilton.htypes import Parallelizable, Collect

from pathlib import Path

from flowerpower.cfg import Config
import requests

####################################################################################################
# Load pipeline parameters. Do not modify this section.

PARAMS = Config.load(
    Path(__file__).parents[1], pipeline_name="hello_world_parallel"
).pipeline.h_params


####################################################################################################
# Helper functions.
# This functions have to start with an underscore (_).


def _list_all_urls() -> list[str]:
    return [
        "https://www.gutenberg.org/files/1342/1342-0.txt",  # Pride and Prejudice
        "https://www.gutenberg.org/files/11/11-0.txt",  # Alice's Adventures in Wonderland
        "https://www.gutenberg.org/files/84/84-0.txt",  # Frankenstein
        "https://www.gutenberg.org/files/98/98-0.txt",  # A Tale of Two Cities
        "https://www.gutenberg.org/files/2701/2701-0.txt",  #
        "https://www.gutenberg.org/files/1232/1232-0.txt",  # The Prince
        "https://www.gutenberg.org/files/74/74-0.txt",  # The Adventures of Tom Sawyer
        "https://www.gutenberg.org/files/5200/5200-0.txt",  # Metamorphosis
        "https://www.gutenberg.org/files/16328/16328-0.txt",  # Beowulf
        "https://www.gutenberg.org/files/55/55-0.txt",  # The Wonderful Wizard of Oz
        "https://www.gutenberg.org/files/1080/1080-0.txt",  # A Modest Proposal
        "https://www.gutenberg.org/files/345/345-0.txt",  # Dracula by Bram Stoker
        "https://www.gutenberg.org/files/174/174-0.txt",  # The Picture of Dorian Gray
        "https://www.gutenberg.org/files/23/23-0.txt",  # The Scarlet Letter
        "https://www.gutenberg.org/files/768/768-0.txt",  # Wuthering Heights by Emily Brontë
        "https://www.gutenberg.org/files/1260/1260-0.txt",  # Jane Eyre by Charlotte Brontë
        "https://www.gutenberg.org/files/1399/1399-0.txt",  # The Iliad by Homer
        "https://www.gutenberg.org/files/135/135-0.txt",  # The Odyssey by Homer
        "https://www.gutenberg.org/files/author/1342.txt",  # The Complete Works of William Shakespeare
        "https://www.gutenberg.org/files/author/11.txt",  # The Complete Works of Lewis Carroll
        "https://www.gutenberg.org/files/author/84.txt",  # The Complete Works of Mary Shelley
        "https://www.gutenberg.org/files/author/98.txt",  # The Complete Works of Charles Dickens
        "https://www.gutenberg.org/files/author/2701.txt",  # The Complete Works of Herman Melville
        "https://www.gutenberg.org/files/author/1232.txt",  # The Complete Works of Niccolò Machiavelli
        "https://www.gutenberg.org/files/author/74.txt",  # The Complete Works of Mark Twain
        "https://www.gutenberg.org/files/author/5200.txt",  # The Complete Works of Franz Kafka
        "https://www.gutenberg.org/files/author/16328.txt",  # The Complete Works of Anonymous
        "https://www.gutenberg.org/files/author/55.txt",  # The Complete Works of L. Frank Baum
        "https://www.gutenberg.org/files/author/1080.txt",  # The Complete Works of Jonathan Swift
        "https://www.gutenberg.org/files/author/345.txt",  # The Complete Works of Bram Stoker
        "https://www.gutenberg.org/files/author/174.txt",  # The Complete Works of Oscar Wilde
        "https://www.gutenberg.org/files/author/23.txt",  # The Complete Works of Nathaniel Hawthorne
        "https://www.gutenberg.org/files/author/768.txt",  # The Complete Works of Emily Brontë
        "https://www.gutenberg.org/files/author/1260.txt",  # The Complete Works of Charlotte Brontë
    ]


def _load(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text


####################################################################################################
# Pipeline functions


def url() -> Parallelizable[str]:
    for url_ in _list_all_urls():
        yield url_


def url_loaded(url: str) -> str:
    return _load(url)


def counts(url_loaded: str) -> int:
    return len(url_loaded.split(" "))


def total_words(counts: Collect[int]) -> int:
    return sum(counts)
