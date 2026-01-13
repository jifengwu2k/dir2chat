# Copyright (c) 2026 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
from __future__ import print_function

import argparse
import codecs
import json
import os.path
import sys
from typing import Iterable, Text, Tuple

from build_filesystem_trie import build_filesystem_trie, iterate_relative_path_components_is_dir_tuples
from cowlist import COWList
from tinytrie import TrieNode


def tree(
        filesystem_trie_node,  # type: TrieNode[str, str]
):
    # type: (...) -> Iterable[str]
    for relative_path_components, is_dir in iterate_relative_path_components_is_dir_tuples(
            filesystem_trie_node=filesystem_trie_node,
    ):
        yield '%s- %s%s' % (
            '  ' * (len(relative_path_components) - 1),
            relative_path_components[-1],
            '/' if is_dir else '',
        )


def iterate_utf_8_plain_text_file_relative_path_components_and_content_tuples(
        prefix,  # type: COWList[str]
        filesystem_trie_node,  # type: TrieNode[str, str]
        max_file_size,  # type: int
):
    # type: (...) -> Iterable[Tuple[COWList[str], Text]]
    for relative_path_components, is_dir in iterate_relative_path_components_is_dir_tuples(
            filesystem_trie_node=filesystem_trie_node,
    ):
        if not is_dir:
            path = os.path.join(*prefix.extend(relative_path_components))
            size = os.path.getsize(path)
            if size <= max_file_size:
                try:
                    with codecs.open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        yield relative_path_components, content
                except UnicodeDecodeError:
                    print('File %r not UTF-8 encoded, skipping' % path, file=sys.stderr)
            else:
                print('File %r size too large, skipping' % path, file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='Generate an OpenAI Chat Completions-compatible JSON from all UTF-8 plaintext files in a directory.'
    )
    parser.add_argument(
        'directory',
        help='Path to the directory to scan.'
    )
    parser.add_argument(
        '-o', '--output',
        default='-',
        help='Output JSON file (default: - for stdout).'
    )
    parser.add_argument(
        '--max-file-size',
        type=int,
        default=65536,
        help='Skip files larger than this size in bytes (default: 65536 or 64 KB).'
    )
    args = parser.parse_args()

    chat_completions_json = []

    prefix, trie = build_filesystem_trie(args.directory)

    tree_result = '\n'.join(tree(filesystem_trie_node=trie))
    chat_completions_json.append(
        {
            "role": "user",
            "content": tree_result,
        }
    )

    for relative_path_components, content in iterate_utf_8_plain_text_file_relative_path_components_and_content_tuples(
            prefix=prefix,
            filesystem_trie_node=trie,
            max_file_size=args.max_file_size,
    ):
        chat_completions_json.append(
            {
                "role": "user",
                "content": '/'.join(relative_path_components),
            }
        )

        chat_completions_json.append(
            {
                "role": "user",
                "content": content,
            }
        )

    if args.output == '-':
        json.dump(chat_completions_json, sys.stdout, indent=2)
        sys.stdout.write('\n')
    else:
        with codecs.open(args.output, 'w', encoding='utf-8') as f:
            json.dump(chat_completions_json, f, indent=2)
            f.write('\n')


if __name__ == '__main__':
    main()
