#
# ContextGem
#
# Copyright 2025 Shcherbak AI AS. All rights reserved. Developed by Sergii Shcherbak.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Base class for the DocxConverter.

This module contains the _DocxConverterBase base class which implements all
the low-level functionality for parsing DOCX files, extracting text, formatting,
tables, images, footnotes, comments, and other elements.
"""

import base64
import re
import xml.etree.ElementTree as ET
from typing import Optional

from contextgem.internal.converters.docx.exceptions import (
    DocxContentError,
    DocxConverterError,
    DocxXmlError,
)
from contextgem.internal.converters.docx.namespaces import WORD_XML_NAMESPACES
from contextgem.internal.converters.docx.package import _DocxPackage
from contextgem.internal.loggers import logger
from contextgem.public.images import Image
from contextgem.public.paragraphs import Paragraph


class _DocxConverterBase:
    """
    Base class for the DOCX converter.
    """

    def _get_style_name(self, style_id: str, package: _DocxPackage) -> str:
        """
        Gets the style name from its ID by looking it up in the styles.xml.

        :param style_id: Style ID to look up
        :param package: _DocxPackage object containing the styles
        :return: Style name or the style_id if not found
        """
        if not style_id:
            return "Normal"

        if package.styles is None:
            return style_id or "Normal"

        try:
            style_element = package.styles.find(
                f".//w:style[@w:styleId='{style_id}']", WORD_XML_NAMESPACES
            )
            if style_element is not None:
                name_element = style_element.find("w:name", WORD_XML_NAMESPACES)
                if name_element is not None and "val" in name_element.attrib.get(
                    f"{{{WORD_XML_NAMESPACES['w']}}}val", ""
                ):
                    return name_element.attrib[f"{{{WORD_XML_NAMESPACES['w']}}}val"]
        except Exception as e:
            # If there's an error finding the style, log it but continue with default
            logger.warning(f"Error looking up style '{style_id}': {str(e)}")

        return style_id or "Normal"

    def _get_paragraph_style(self, para_element: ET.Element) -> str:
        """
        Extracts the style information from a paragraph element.

        :param para_element: Paragraph XML element
        :return: Style ID string
        """
        # Find the paragraph properties element
        p_pr = para_element.find("w:pPr", WORD_XML_NAMESPACES)
        if p_pr is not None:
            # Find the style element within paragraph properties
            style = p_pr.find("w:pStyle", WORD_XML_NAMESPACES)
            if (
                style is not None
                and f"{{{WORD_XML_NAMESPACES['w']}}}val" in style.attrib
            ):
                return style.attrib[f"{{{WORD_XML_NAMESPACES['w']}}}val"]

        return "Normal"

    def _get_list_info(
        self, para_element: ET.Element, package: _DocxPackage
    ) -> tuple[bool, int, str, str, bool]:
        """
        Extracts list information from a paragraph element.

        :param para_element: Paragraph XML element
        :param package: _DocxPackage object
        :return: Tuple of (is_list, list_level, list_info_string, list_type, is_numbered)
        """
        is_list = False
        list_level = 0
        list_info = ""
        list_type = ""
        is_numbered = False

        p_pr = para_element.find("w:pPr", WORD_XML_NAMESPACES)
        if p_pr is not None:
            num_pr = p_pr.find("w:numPr", WORD_XML_NAMESPACES)
            if num_pr is not None:
                is_list = True

                # Get list ID
                num_id_elem = num_pr.find("w:numId", WORD_XML_NAMESPACES)
                num_id = (
                    num_id_elem.attrib[f"{{{WORD_XML_NAMESPACES['w']}}}val"]
                    if num_id_elem is not None
                    else None
                )

                # Get level
                ilvl_elem = num_pr.find("w:ilvl", WORD_XML_NAMESPACES)
                if ilvl_elem is not None:
                    list_level = int(
                        ilvl_elem.attrib[f"{{{WORD_XML_NAMESPACES['w']}}}val"]
                    )

                # Determine list type and numbering format if numbering is available
                if num_id and package.numbering is not None:
                    # First find the abstractNumId associated with this numId
                    num_def = package.numbering.find(
                        f".//w:num[@w:numId='{num_id}']", WORD_XML_NAMESPACES
                    )
                    if num_def is not None:
                        abstract_num_id_elem = num_def.find(
                            "w:abstractNumId", WORD_XML_NAMESPACES
                        )
                        if abstract_num_id_elem is not None:
                            abstract_num_id = abstract_num_id_elem.attrib[
                                f"{{{WORD_XML_NAMESPACES['w']}}}val"
                            ]

                            # Now find the level formatting in the abstractNum
                            abstract_num = package.numbering.find(
                                f".//w:abstractNum[@w:abstractNumId='{abstract_num_id}']",
                                WORD_XML_NAMESPACES,
                            )
                            if abstract_num is not None:
                                # Find the level formatting for this specific level
                                level_elem = abstract_num.find(
                                    f".//w:lvl[@w:ilvl='{list_level}']",
                                    WORD_XML_NAMESPACES,
                                )
                                if level_elem is not None:
                                    # Get the numFmt element which defines if it's bullet or numbered
                                    num_fmt = level_elem.find(
                                        "w:numFmt", WORD_XML_NAMESPACES
                                    )
                                    if (
                                        num_fmt is not None
                                        and f"{{{WORD_XML_NAMESPACES['w']}}}val"
                                        in num_fmt.attrib
                                    ):
                                        fmt_val = num_fmt.attrib[
                                            f"{{{WORD_XML_NAMESPACES['w']}}}val"
                                        ]
                                        list_type = fmt_val

                                        # Check if it's a numbered list format
                                        numbered_formats = {
                                            "decimal",
                                            "decimalZero",
                                            "upperRoman",
                                            "lowerRoman",
                                            "upperLetter",
                                            "lowerLetter",
                                            "ordinal",
                                            "cardinalText",
                                            "ordinalText",
                                            "hex",
                                            "chicago",
                                            "ideographDigital",
                                            "japaneseCounting",
                                            "aiueo",
                                            "iroha",
                                            "arabicFullWidth",
                                            "hindiNumbers",
                                            "thaiNumbers",
                                        }
                                        is_numbered = fmt_val in numbered_formats

                if num_id:
                    list_info = f", List ID: {num_id}, Level: {list_level}"
                    if list_type:
                        list_info += f", Format: {list_type}"

        return is_list, list_level, list_info, list_type, is_numbered

    def _extract_footnote_references(self, para_element: ET.Element) -> list[str]:
        """
        Extracts footnote references from a paragraph.

        :param para_element: Paragraph XML element
        :return: List of footnote IDs
        """
        footnote_ids = []

        # Find all footnote references in this paragraph
        for run in para_element.findall(".//w:r", WORD_XML_NAMESPACES):
            footnote_ref = run.find(".//w:footnoteReference", WORD_XML_NAMESPACES)
            if (
                footnote_ref is not None
                and f"{{{WORD_XML_NAMESPACES['w']}}}id" in footnote_ref.attrib
            ):
                footnote_id = footnote_ref.attrib[f"{{{WORD_XML_NAMESPACES['w']}}}id"]
                footnote_ids.append(footnote_id)

        return footnote_ids

    def _extract_comment_references(self, para_element: ET.Element) -> list[str]:
        """
        Extracts comment references from a paragraph.

        :param para_element: Paragraph XML element
        :return: List of comment IDs
        """
        comment_ids = []

        # Find all comment references in this paragraph
        for run in para_element.findall(".//w:r", WORD_XML_NAMESPACES):
            comment_ref = run.find(".//w:commentReference", WORD_XML_NAMESPACES)
            if (
                comment_ref is not None
                and f"{{{WORD_XML_NAMESPACES['w']}}}id" in comment_ref.attrib
            ):
                comment_id = comment_ref.attrib[f"{{{WORD_XML_NAMESPACES['w']}}}id"]
                comment_ids.append(comment_id)

        return comment_ids

    def _process_footnotes(
        self,
        package: _DocxPackage,
        strict_mode: bool = False,
        include_textboxes: bool = True,
    ) -> list[Paragraph]:
        """
        Processes footnotes from the footnotes.xml file and converts them to Paragraph objects.

        :param package: _DocxPackage object
        :param strict_mode: If True, raise exceptions for any processing error
            instead of skipping problematic elements (default: False)
        :param include_textboxes: If True, include textbox content (default: True)
        :return: List of Paragraph objects representing footnotes
        """
        footnote_paragraphs = []

        if package.footnotes is None:
            return footnote_paragraphs

        # Find all footnote elements (excluding separators and continuation separators)
        for footnote_elem in package.footnotes.findall(
            ".//w:footnote", WORD_XML_NAMESPACES
        ):
            # Skip special footnotes (separators and continuation notices)
            if f"{{{WORD_XML_NAMESPACES['w']}}}id" not in footnote_elem.attrib:
                continue

            footnote_id = footnote_elem.attrib[f"{{{WORD_XML_NAMESPACES['w']}}}id"]
            if footnote_id in ("-1", "0"):  # Separator and continuation separator
                continue

            # Process each paragraph in the footnote
            for para in footnote_elem.findall(".//w:p", WORD_XML_NAMESPACES):
                # Extract the text content
                para_text = self._extract_paragraph_text(
                    para, strict_mode=strict_mode, include_textboxes=include_textboxes
                ).strip()
                if para_text:
                    # Get paragraph style and metadata
                    style_id = self._get_paragraph_style(para)
                    style_name = self._get_style_name(style_id, package)

                    # Include footnote ID in the metadata
                    footnote_info = f"Style: {style_name}, Footnote: {footnote_id}"

                    # Create paragraph object with metadata
                    footnote_paragraphs.append(
                        Paragraph(raw_text=para_text, additional_context=footnote_info)
                    )

        return footnote_paragraphs

    def _process_comments(
        self,
        package: _DocxPackage,
        strict_mode: bool = False,
        include_textboxes: bool = True,
    ) -> list[Paragraph]:
        """
        Processes comments from the comments.xml file and converts them to Paragraph objects.

        :param package: _DocxPackage object
        :param strict_mode: If True, raise exceptions for any processing error
            instead of skipping problematic elements (default: False)
        :param include_textboxes: If True, include textbox content (default: True)
        :return: List of Paragraph objects representing comments
        """
        comment_paragraphs = []

        if package.comments is None:
            return comment_paragraphs

        # Find all comment elements with explicit namespace
        comment_elements = package.comments.findall(
            f".//{{{WORD_XML_NAMESPACES['w']}}}comment", WORD_XML_NAMESPACES
        )

        for comment_elem in comment_elements:
            # Skip comments without an ID
            if f"{{{WORD_XML_NAMESPACES['w']}}}id" not in comment_elem.attrib:
                continue

            comment_id = comment_elem.attrib[f"{{{WORD_XML_NAMESPACES['w']}}}id"]

            # Get comment author if available
            author = ""
            if f"{{{WORD_XML_NAMESPACES['w']}}}author" in comment_elem.attrib:
                author = comment_elem.attrib[f"{{{WORD_XML_NAMESPACES['w']}}}author"]

            # Get comment date if available
            date = ""
            if f"{{{WORD_XML_NAMESPACES['w']}}}date" in comment_elem.attrib:
                date = comment_elem.attrib[f"{{{WORD_XML_NAMESPACES['w']}}}date"]

            # Process each paragraph in the comment with explicit namespace
            for para in comment_elem.findall(
                f".//{{{WORD_XML_NAMESPACES['w']}}}p", WORD_XML_NAMESPACES
            ):
                # Extract the text content
                para_text = self._extract_paragraph_text(
                    para, strict_mode=strict_mode, include_textboxes=include_textboxes
                ).strip()
                if para_text:
                    # Get paragraph style and metadata
                    style_id = self._get_paragraph_style(para)
                    style_name = self._get_style_name(style_id, package)

                    # Build metadata
                    comment_info = f"Style: {style_name}, Comment: {comment_id}"
                    if author:
                        comment_info += f", Author: {author}"
                    if date:
                        comment_info += f", Date: {date}"

                    # Create paragraph object with metadata
                    comment_paragraphs.append(
                        Paragraph(raw_text=para_text, additional_context=comment_info)
                    )

        return comment_paragraphs

    def _extract_paragraph_text(
        self,
        para_element: ET.Element,
        strict_mode: bool = False,
        include_textboxes: bool = True,
    ) -> str:
        """
        Extracts the text content from a paragraph element.

        :param para_element: Paragraph XML element
        :param strict_mode: If True, raise exceptions for any processing error
            instead of skipping problematic elements (default: False)
        :param include_textboxes: If True, include textbox content (default: True)
        :return: Text content of the paragraph
        """
        # Use a dictionary to track text content by location
        text_by_location = {}
        ordered_runs = []

        # Track processed element IDs to avoid technical duplicates
        processed_elem_ids = set()

        try:
            # Process regular paragraph text first (most common case)
            run_idx = 0
            for run in para_element.findall(".//w:r", WORD_XML_NAMESPACES):
                # Skip runs that are part of drawings (we'll handle them separately)
                if run.find(".//w:drawing", WORD_XML_NAMESPACES) is not None:
                    continue

                # Process text elements in this run
                for text_elem in run.findall(".//w:t", WORD_XML_NAMESPACES):
                    elem_id = id(text_elem)
                    if text_elem.text and elem_id not in processed_elem_ids:
                        text_by_location[run_idx] = text_elem.text
                        ordered_runs.append(run_idx)
                        processed_elem_ids.add(elem_id)
                        run_idx += 1

                # Process line breaks in this run
                for br in run.findall(".//w:br", WORD_XML_NAMESPACES):
                    text_by_location[run_idx] = "\n"
                    ordered_runs.append(run_idx)
                    run_idx += 1

                # Add footnote reference marker if this run contains a footnote reference
                footnote_ref = run.find(".//w:footnoteReference", WORD_XML_NAMESPACES)
                if (
                    footnote_ref is not None
                    and f"{{{WORD_XML_NAMESPACES['w']}}}id" in footnote_ref.attrib
                ):
                    footnote_id = footnote_ref.attrib[
                        f"{{{WORD_XML_NAMESPACES['w']}}}id"
                    ]
                    text_by_location[run_idx] = (
                        f"[Footnote {footnote_id}]"  # Use footnote ID as marker
                    )
                    ordered_runs.append(run_idx)
                    run_idx += 1

                # Add comment reference marker if this run contains a comment reference
                comment_ref = run.find(".//w:commentReference", WORD_XML_NAMESPACES)
                if (
                    comment_ref is not None
                    and f"{{{WORD_XML_NAMESPACES['w']}}}id" in comment_ref.attrib
                ):
                    comment_id = comment_ref.attrib[f"{{{WORD_XML_NAMESPACES['w']}}}id"]
                    text_by_location[run_idx] = (
                        f"[Comment {comment_id}]"  # Use comment ID as marker
                    )
                    ordered_runs.append(run_idx)
                    run_idx += 1

            # Process drawing objects (incl. text boxes) - these need special handling
            # Skip this section if include_textboxes is False
            if include_textboxes:
                # We keep track of which drawings we've seen to avoid duplicates but still permit
                # intentional repetition of text boxes

                # Group 1: Standard VML textboxes
                vml_idx = 1000
                for textbox in para_element.findall(
                    ".//v:textbox", WORD_XML_NAMESPACES
                ):
                    for text_elem in textbox.findall(".//w:t", WORD_XML_NAMESPACES):
                        elem_id = id(text_elem)
                        if text_elem.text and elem_id not in processed_elem_ids:
                            text_by_location[vml_idx] = text_elem.text
                            ordered_runs.append(vml_idx)
                            processed_elem_ids.add(elem_id)
                            vml_idx += 1

                # Group 2: DrawingML textboxes (Office 2007+ format)
                dml_idx = 2000
                txbx_content_elems = para_element.findall(
                    ".//w:txbxContent", WORD_XML_NAMESPACES
                )
                for txbx_content in txbx_content_elems:
                    # Process each paragraph in the text box content
                    for p in txbx_content.findall(".//w:p", WORD_XML_NAMESPACES):
                        for text_elem in p.findall(".//w:t", WORD_XML_NAMESPACES):
                            elem_id = id(text_elem)
                            if text_elem.text and elem_id not in processed_elem_ids:
                                text_by_location[dml_idx] = text_elem.text
                                ordered_runs.append(dml_idx)
                                processed_elem_ids.add(elem_id)
                                dml_idx += 1

                # Group 3: DrawingML text directly in shapes
                shape_idx = 3000
                for text_elem in para_element.findall(".//a:t", WORD_XML_NAMESPACES):
                    elem_id = id(text_elem)
                    if text_elem.text and elem_id not in processed_elem_ids:
                        text_by_location[shape_idx] = text_elem.text
                        ordered_runs.append(shape_idx)
                        processed_elem_ids.add(elem_id)
                        shape_idx += 1

                # Group 4: Drawing elements that might contain text not captured by other groups
                drawing_idx = 4000
                for drawing in para_element.findall(
                    ".//w:drawing", WORD_XML_NAMESPACES
                ):
                    # Extract any text elements that might be in the drawing but not covered by previous groups
                    for text_elem in drawing.findall(".//w:t", WORD_XML_NAMESPACES):
                        elem_id = id(text_elem)
                        if text_elem.text and elem_id not in processed_elem_ids:
                            text_by_location[drawing_idx] = text_elem.text
                            ordered_runs.append(drawing_idx)
                            processed_elem_ids.add(elem_id)
                            drawing_idx += 1

            # Group 5: Handle Markup Compatibility (mc) alternate content
            # This is crucial because Word often uses this for cross-version compatibility
            # and the same content can appear in both the Choice and Fallback sections
            mc_idx = 5000
            for mc_elem in para_element.findall(
                ".//mc:AlternateContent", WORD_XML_NAMESPACES
            ):
                # First try the Choice content (preferred for newer versions of Word)
                choice_elems = mc_elem.findall(".//mc:Choice", WORD_XML_NAMESPACES)
                fallback_elems = mc_elem.findall(".//mc:Fallback", WORD_XML_NAMESPACES)

                # We only want to process either Choice OR Fallback, not both, as they represent
                # alternate representations of the same content
                if choice_elems:
                    for choice in choice_elems:
                        # If include_textboxes is False, skip textboxes in markup compatibility content
                        if not include_textboxes:
                            # Skip textbox content within this choice element
                            has_textbox = (
                                choice.find(".//v:textbox", WORD_XML_NAMESPACES)
                                is not None
                                or choice.find(".//w:txbxContent", WORD_XML_NAMESPACES)
                                is not None
                                or choice.find(".//a:t", WORD_XML_NAMESPACES)
                                is not None
                                or choice.find(".//w:drawing", WORD_XML_NAMESPACES)
                                is not None
                            )
                            if has_textbox:
                                continue

                        for text_elem in choice.findall(".//w:t", WORD_XML_NAMESPACES):
                            elem_id = id(text_elem)
                            if text_elem.text and elem_id not in processed_elem_ids:
                                text_by_location[mc_idx] = text_elem.text
                                ordered_runs.append(mc_idx)
                                processed_elem_ids.add(elem_id)
                                mc_idx += 1
                # Only use Fallback if we didn't find any usable Choice elements
                elif fallback_elems:
                    # Check if we've already extracted text from a Choice element
                    for fallback in fallback_elems:
                        # If include_textboxes is False, skip textboxes in markup compatibility content
                        if not include_textboxes:
                            # Skip textbox content within this fallback element
                            has_textbox = (
                                fallback.find(".//v:textbox", WORD_XML_NAMESPACES)
                                is not None
                                or fallback.find(
                                    ".//w:txbxContent", WORD_XML_NAMESPACES
                                )
                                is not None
                                or fallback.find(".//a:t", WORD_XML_NAMESPACES)
                                is not None
                                or fallback.find(".//w:drawing", WORD_XML_NAMESPACES)
                                is not None
                            )
                            if has_textbox:
                                continue

                        for text_elem in fallback.findall(
                            ".//w:t", WORD_XML_NAMESPACES
                        ):
                            elem_id = id(text_elem)
                            if text_elem.text and elem_id not in processed_elem_ids:
                                text_by_location[mc_idx] = text_elem.text
                                ordered_runs.append(mc_idx)
                                processed_elem_ids.add(elem_id)
                                mc_idx += 1

            # Sort the runs to maintain document order
            ordered_runs.sort()

            # Get raw text parts
            text_parts = [text_by_location[idx] for idx in ordered_runs]

            # Post-processing step: fix text box duplication where identical text appears consecutively
            # This handles cases where Word stores the same text multiple times in the XML
            processed_text = []
            i = 0
            while i < len(text_parts):
                # Start with the current text segment
                current_segment = text_parts[i]

                # Check if the same text is immediately repeated (common in text boxes)
                j = i + 1
                while j < len(text_parts) and text_parts[j] == current_segment:
                    # Skip consecutive identical segments
                    j += 1

                # Add the text segment once and skip all duplicates
                processed_text.append(current_segment)
                i = j

            return "".join(processed_text)
        except Exception as e:
            if strict_mode:
                raise DocxContentError(
                    f"Error extracting paragraph text: {str(e)}"
                ) from e
            else:
                logger.warning(f"Error extracting paragraph text: {str(e)}")
                return ""

    def _is_text_box_paragraph(self, para_element: ET.Element) -> bool:
        """
        Determines if a paragraph is from a text box.

        :param para_element: Paragraph XML element
        :return: True if the paragraph is part of a text box
        """
        # Check for various types of text boxes in Word
        # 1. VML textbox (older Word format)
        if para_element.find(".//v:textbox", WORD_XML_NAMESPACES) is not None:
            return True

        # 2. DrawingML text box (Office 2007+)
        if para_element.find(".//w:txbxContent", WORD_XML_NAMESPACES) is not None:
            return True

        # 3. Check for shape with text
        if para_element.find(".//a:t", WORD_XML_NAMESPACES) is not None:
            return True

        # 4. Check for drawing element
        if para_element.find(".//w:drawing", WORD_XML_NAMESPACES) is not None:
            return True

        return False

    def _process_paragraph(
        self,
        para_element: ET.Element,
        package: _DocxPackage,
        markdown_mode: bool = False,
        strict_mode: bool = False,
        include_textboxes: bool = True,
    ) -> Optional[str | Paragraph]:
        """
        Processes a paragraph element and returns either a markdown string or Paragraph object.

        :param para_element: Paragraph XML element
        :param package: _DocxPackage object
        :param markdown_mode: If True, return markdown formatted text,
            otherwise return a Paragraph object (default: False)
        :param strict_mode: If True, raise exceptions for any processing error
            instead of skipping problematic elements (default: False)
        :param include_textboxes: If True, include textbox content (default: True)
        :return: Markdown string, Paragraph object, or None if paragraph is empty
        """
        try:
            # Check if this is a text box paragraph and we should skip it
            if not include_textboxes and self._is_text_box_paragraph(para_element):
                return None

            # Extract text content
            text = self._extract_paragraph_text(
                para_element,
                strict_mode=strict_mode,
                include_textboxes=include_textboxes,
            ).strip()
            if not text:
                return None

            # Get style information
            style_id = self._get_paragraph_style(para_element)
            style_name = self._get_style_name(style_id, package)
            style_info = f"Style: {style_name}"

            # Get list information
            is_list, list_level, _, list_type, is_numbered = self._get_list_info(
                para_element, package
            )

            # Get footnote reference information
            footnote_info = ""
            footnote_ids = self._extract_footnote_references(para_element)
            if footnote_ids:
                footnote_info = f", Footnote References: {','.join(footnote_ids)}"

            # Get comment reference information
            comment_info = ""
            comment_ids = self._extract_comment_references(para_element)
            if comment_ids:
                comment_info = f", Comment References: {','.join(comment_ids)}"

            # Check if this is a text box paragraph
            text_box_info = ""
            if self._is_text_box_paragraph(para_element):
                text_box_info = ", Text Box"

            if markdown_mode:
                # Convert to markdown based on style and list status
                if style_name.lower().startswith("heading"):
                    # Extract heading level (e.g., "Heading 1" -> 1)
                    heading_level = 1
                    match = re.search(r"(\d+)", style_name)
                    if match:
                        heading_level = int(match.group(1))
                    return "#" * heading_level + " " + text

                elif is_list:
                    # Add indentation based on list level
                    indent = "    " * list_level

                    # Use the appropriate list marker based on list type
                    if is_numbered:
                        # For numbered lists, use "1. " format
                        # Note: Markdown doesn't support different numbered formats,
                        # but it will render as a numbered list
                        return f"{indent}1. {text}"
                    else:
                        # For bullet lists, use "- " format
                        return f"{indent}- {text}"

                else:
                    # Regular paragraph
                    return text
            else:
                # Return a Paragraph instance with metadata
                metadata = style_info

                # Add list information with more details
                if is_list:
                    list_type_info = "Numbered" if is_numbered else "Bullet"
                    metadata += f", List Type: {list_type_info}, Level: {list_level}"
                    if list_type:
                        metadata += f", Format: {list_type}"

                    # Extract List ID from original _get_list_info results
                    p_pr = para_element.find("w:pPr", WORD_XML_NAMESPACES)
                    if p_pr is not None:
                        num_pr = p_pr.find("w:numPr", WORD_XML_NAMESPACES)
                        if num_pr is not None:
                            num_id_elem = num_pr.find("w:numId", WORD_XML_NAMESPACES)
                            if num_id_elem is not None:
                                list_id = num_id_elem.attrib[
                                    f"{{{WORD_XML_NAMESPACES['w']}}}val"
                                ]
                                metadata += f", List ID: {list_id}"

                metadata += footnote_info + comment_info + text_box_info
                return Paragraph(raw_text=text, additional_context=metadata)
        except DocxXmlError:
            # Re-raise specific XML errors
            raise
        except Exception as e:
            if strict_mode:
                raise DocxContentError(f"Error processing paragraph: {str(e)}") from e
            else:
                logger.warning(f"Error processing paragraph: {str(e)}")
                return None

    def _process_table(
        self,
        table_element: ET.Element,
        package: _DocxPackage,
        markdown_mode: bool = False,
        table_idx: int = 0,
        strict_mode: bool = False,
        include_textboxes: bool = True,
    ) -> list[str | Paragraph]:
        """
        Processes a table element and returns either paragraphs or markdown lines.

        :param table_element: Table XML element
        :param package: _DocxPackage object
        :param markdown_mode: If True, return markdown formatted lines,
            otherwise return Paragraph objects (default: False)
        :param table_idx: Index of the table in the document (default: 0)
        :param strict_mode: If True, raise exceptions for any processing error
            instead of skipping problematic elements (default: False)
        :param include_textboxes: If True, include textbox content (default: True)
        :return: List of markdown lines or Paragraph objects
        """
        result = []

        try:
            if markdown_mode:
                # Process table for markdown output
                rows = table_element.findall(".//w:tr", WORD_XML_NAMESPACES)
                if not rows:
                    return result

                # Collect all cell data and determine column widths
                all_rows = []
                col_widths = []

                for row in rows:
                    row_cells = []
                    for cell in row.findall(".//w:tc", WORD_XML_NAMESPACES):
                        # Combine all text from paragraphs in the cell
                        cell_text = []
                        for para in cell.findall(".//w:p", WORD_XML_NAMESPACES):
                            # Process paragraph
                            processed_para = self._process_paragraph(
                                para, package, True, strict_mode, include_textboxes
                            )
                            if processed_para:
                                cell_text.append(processed_para)

                        cell_content = " ".join(cell_text).strip() or " "
                        row_cells.append(cell_content)

                    all_rows.append(row_cells)

                    # Update max widths
                    if not col_widths:
                        col_widths = [len(cell) for cell in row_cells]
                    else:
                        for i, cell in enumerate(row_cells):
                            if i < len(col_widths):
                                col_widths[i] = max(col_widths[i], len(cell))

                # Format the table as markdown
                for row_idx, row_cells in enumerate(all_rows):
                    # Pad cells for alignment
                    padded_cells = []
                    for i, cell in enumerate(row_cells):
                        if i < len(col_widths):
                            padded_cells.append(cell.ljust(col_widths[i]))
                        else:
                            padded_cells.append(cell)

                    result.append("| " + " | ".join(padded_cells) + " |")

                    # Add header separator after first row
                    if row_idx == 0:
                        separator = []
                        for width in col_widths[: len(row_cells)]:
                            separator.append("-" * width)
                        result.append("| " + " | ".join(separator) + " |")

                # Add blank line after table
                result.append("")
            else:
                # Process table for Paragraph objects
                table_metadata = f"Table: {table_idx+1}"
                rows = table_element.findall(".//w:tr", WORD_XML_NAMESPACES)

                for row_idx, row in enumerate(rows):
                    for cell_idx, cell in enumerate(
                        row.findall(".//w:tc", WORD_XML_NAMESPACES)
                    ):
                        for para in cell.findall(".//w:p", WORD_XML_NAMESPACES):
                            # Process paragraph
                            processed_para = self._process_paragraph(
                                para, package, False, strict_mode, include_textboxes
                            )
                            if processed_para:
                                style_id = self._get_paragraph_style(para)
                                style_name = self._get_style_name(style_id, package)
                                cell_style_info = f"Style: {style_name}"

                                # Copy the paragraph with added table metadata
                                cell_para = Paragraph(
                                    raw_text=processed_para.raw_text,
                                    additional_context=f"{cell_style_info}, {table_metadata}, "
                                    f"Row: {row_idx+1}, Column: {cell_idx+1}, "
                                    f"Table Cell"
                                    + (
                                        ", "
                                        + processed_para.additional_context.split(
                                            ", ", 1
                                        )[1]
                                        if ", " in processed_para.additional_context
                                        else ""
                                    ),
                                )
                                result.append(cell_para)

            return result
        except Exception as e:
            # Handle table parsing errors
            if isinstance(e, DocxConverterError):
                # Re-raise specific converter errors
                raise
            else:
                if strict_mode:
                    raise DocxContentError(f"Error processing table: {str(e)}") from e
                else:
                    logger.warning(
                        f"Error processing table (idx: {table_idx}): {str(e)}"
                    )
                    # Return whatever we've processed so far
                    return result

    def _process_headers(
        self,
        package: _DocxPackage,
        strict_mode: bool = False,
        include_textboxes: bool = True,
    ) -> list[Paragraph]:
        """
        Processes headers from the header XML files and converts them to Paragraph objects.

        :param package: _DocxPackage object
        :param strict_mode: If True, raise exceptions for any processing error
            instead of skipping problematic elements (default: False)
        :param include_textboxes: If True, include textbox content (default: True)
        :return: List of Paragraph objects representing headers
        """
        header_paragraphs = []

        if not package.headers:
            return header_paragraphs

        # Process each header
        for header_id, header_info in package.headers.items():
            header_content = header_info["content"]

            # Process each paragraph in the header
            for para in header_content.findall(
                f".//{{{WORD_XML_NAMESPACES['w']}}}p", WORD_XML_NAMESPACES
            ):
                # Extract the text content
                para_text = self._extract_paragraph_text(
                    para, strict_mode=strict_mode, include_textboxes=include_textboxes
                ).strip()
                if para_text:
                    # Get paragraph style and metadata
                    style_id = self._get_paragraph_style(para)
                    style_name = self._get_style_name(style_id, package)

                    # Build metadata
                    header_info = f"Style: {style_name}, Header: {header_id}"

                    # Create paragraph object with metadata
                    header_paragraphs.append(
                        Paragraph(raw_text=para_text, additional_context=header_info)
                    )

        return header_paragraphs

    def _process_footers(
        self,
        package: _DocxPackage,
        strict_mode: bool = False,
        include_textboxes: bool = True,
    ) -> list[Paragraph]:
        """
        Processes footers from the footer XML files and converts them to Paragraph objects.

        :param package: _DocxPackage object
        :param strict_mode: If True, raise exceptions for any processing error
            instead of skipping problematic elements (default: False)
        :param include_textboxes: If True, include textbox content (default: True)
        :return: List of Paragraph objects representing footers
        """
        footer_paragraphs = []

        if not package.footers:
            return footer_paragraphs

        # Process each footer
        for footer_id, footer_info in package.footers.items():
            footer_content = footer_info["content"]

            # Process each paragraph in the footer
            for para in footer_content.findall(
                f".//{{{WORD_XML_NAMESPACES['w']}}}p", WORD_XML_NAMESPACES
            ):
                # Extract the text content
                para_text = self._extract_paragraph_text(
                    para, strict_mode=strict_mode, include_textboxes=include_textboxes
                ).strip()
                if para_text:
                    # Get paragraph style and metadata
                    style_id = self._get_paragraph_style(para)
                    style_name = self._get_style_name(style_id, package)

                    # Build metadata
                    footer_info = f"Style: {style_name}, Footer: {footer_id}"

                    # Create paragraph object with metadata
                    footer_paragraphs.append(
                        Paragraph(raw_text=para_text, additional_context=footer_info)
                    )

        return footer_paragraphs

    def _process_docx_elements(
        self,
        package: _DocxPackage,
        markdown_mode: bool = False,
        include_tables: bool = True,
        include_comments: bool = True,
        include_footnotes: bool = True,
        include_headers: bool = True,
        include_footers: bool = True,
        include_textboxes: bool = True,
        strict_mode: bool = False,
    ) -> list[str | Paragraph]:
        """
        Processes all elements in the DOCX document and returns appropriate objects.

        :param package: _DocxPackage object
        :param markdown_mode: If True, return markdown formatted lines,
            otherwise return objects (default: False)
        :param include_tables: If True, include tables in the output (default: True)
        :param include_comments: If True, include comments in the output (default: True)
        :param include_footnotes: If True, include footnotes in the output (default: True)
        :param include_headers: If True, include headers in the output (default: True)
        :param include_footers: If True, include footers in the output (default: True)
        :param include_textboxes: If True, include textbox content (default: True)
        :param strict_mode: If True, raise exceptions for any processing
            error instead of skipping problematic elements (default: False)
        :return: List of markdown lines or Paragraph objects
        """
        result = []

        if package.main_document is None:
            raise DocxContentError("Main document content is missing")

        try:
            # Get the body element
            body = package.main_document.find(
                f".//{{{WORD_XML_NAMESPACES['w']}}}body", WORD_XML_NAMESPACES
            )
            if body is None:
                raise DocxContentError("Document body element is missing")

            # Process headers
            if include_headers:
                try:
                    header_paragraphs = self._process_headers(
                        package,
                        strict_mode=strict_mode,
                        include_textboxes=include_textboxes,
                    )
                    if markdown_mode and header_paragraphs:
                        for para in header_paragraphs:
                            # Add clear Header marker
                            result.append(f"**Header**: {para.raw_text}")
                            result.append("")
                    else:
                        # For object mode, add headers at the beginning
                        result.extend(header_paragraphs)
                except Exception as e:
                    # In strict mode, re-raise as DocxContentError
                    if strict_mode:
                        raise DocxContentError(
                            f"Error processing headers: {str(e)}"
                        ) from e
                    # Otherwise, log error and continue without headers
                    logger.warning(f"Error processing headers: {str(e)}")

            # Track tables for indexing
            table_count = 0

            # Track numbered lists for proper sequencing in markdown mode
            list_counters = {}  # {(list_id, level): counter}
            last_list_id = None
            last_list_level = -1

            # Process each element in order
            for element in body:
                tag = element.tag.split("}")[-1]  # Remove namespace prefix

                if tag == "p":
                    # Process paragraph
                    try:
                        # Before processing, check if this is a list item that needs
                        # special handling for markdown
                        if markdown_mode:
                            # Extract list information
                            p_pr = element.find("w:pPr", WORD_XML_NAMESPACES)
                            if p_pr is not None:
                                num_pr = p_pr.find("w:numPr", WORD_XML_NAMESPACES)
                                if num_pr is not None:
                                    # This is a list item
                                    _, list_level, __, ___, is_numbered = (
                                        self._get_list_info(element, package)
                                    )

                                    # Get num_id for this list item
                                    num_id_elem = num_pr.find(
                                        "w:numId", WORD_XML_NAMESPACES
                                    )
                                    if num_id_elem is not None:
                                        num_id = num_id_elem.attrib[
                                            f"{{{WORD_XML_NAMESPACES['w']}}}val"
                                        ]

                                        # If it's a numbered list, we need to track counter
                                        if is_numbered:
                                            list_key = (num_id, list_level)

                                            # Reset counter if this is a new list or a higher
                                            # level in the same list
                                            if (
                                                last_list_id != num_id
                                                or list_level < last_list_level
                                            ):
                                                # Reset counters for all levels below
                                                # the current level
                                                for key in list(list_counters.keys()):
                                                    if (
                                                        key[0] == num_id
                                                        and key[1] > list_level
                                                    ):
                                                        list_counters.pop(key)

                                            # Initialize counter if needed
                                            if list_key not in list_counters:
                                                list_counters[list_key] = 1
                                            else:
                                                list_counters[list_key] += 1

                                            # Remember this list for next iteration
                                            last_list_id = num_id
                                            last_list_level = list_level

                                            # Now extract paragraph text to build the markdown
                                            text = self._extract_paragraph_text(
                                                element,
                                                strict_mode=strict_mode,
                                                include_textboxes=include_textboxes,
                                            ).strip()
                                            if text:
                                                # Add indentation based on list level
                                                indent = "    " * list_level
                                                # Use actual number from counter
                                                result.append(
                                                    f"{indent}{list_counters[list_key]}. {text}"
                                                )
                                                result.append("")  # Add blank line
                                                continue  # Skip normal processing

                        # Regular processing for non-numbered lists or non-markdown mode
                        processed_para = self._process_paragraph(
                            element,
                            package,
                            markdown_mode,
                            strict_mode,
                            include_textboxes,
                        )
                        if processed_para is not None:
                            result.append(processed_para)
                            # Add blank line after paragraphs in markdown mode
                            if markdown_mode:
                                result.append("")
                    except Exception as e:
                        if strict_mode:
                            # In strict mode, re-raise as DocxContentError
                            raise DocxContentError(
                                f"Error processing paragraph: {str(e)}"
                            )
                        # Log error and continue with next paragraph
                        logger.warning(f"Error processing paragraph: {str(e)}")

                elif tag == "tbl" and include_tables:
                    # Process table
                    try:
                        table_items = self._process_table(
                            element,
                            package,
                            markdown_mode,
                            table_count,
                            strict_mode,
                            include_textboxes,
                        )
                        result.extend(table_items)
                        table_count += 1
                    except Exception as e:
                        if strict_mode:
                            # In strict mode, re-raise as DocxContentError
                            raise DocxContentError(
                                f"Error processing table: {str(e)}"
                            ) from e
                        # Log error and continue with next element
                        logger.warning(f"Error processing table: {str(e)}")

            # Process footnotes and add them as regular paragraphs
            if include_footnotes and package.footnotes is not None:
                try:
                    footnote_paragraphs = self._process_footnotes(
                        package,
                        strict_mode=strict_mode,
                        include_textboxes=include_textboxes,
                    )

                    if markdown_mode and footnote_paragraphs:
                        # Add each footnote as markdown text
                        for para in footnote_paragraphs:
                            footnote_id = para.additional_context.split("Footnote: ")[
                                1
                            ].split(",")[0]
                            result.append(
                                f"**Footnote {footnote_id}**: {para.raw_text}"
                            )
                            result.append("")
                    else:
                        # For object mode, just add footnotes as paragraphs
                        result.extend(footnote_paragraphs)
                except Exception as e:
                    if strict_mode:
                        # In strict mode, re-raise as DocxContentError
                        raise DocxContentError(
                            f"Error processing footnotes: {str(e)}"
                        ) from e
                    # Log error and continue without footnotes
                    logger.warning(f"Error processing footnotes: {str(e)}")

            # Process comments and add them as regular paragraphs
            if include_comments and package.comments is not None:
                try:
                    comment_paragraphs = self._process_comments(
                        package,
                        strict_mode=strict_mode,
                        include_textboxes=include_textboxes,
                    )

                    if markdown_mode and comment_paragraphs:
                        # Add each comment as markdown text
                        for para in comment_paragraphs:
                            if "Comment:" in para.additional_context:
                                # Extract comment ID from additional_context
                                comment_id = para.additional_context.split("Comment: ")[
                                    1
                                ].split(",")[0]

                                # Extract author if present
                                author = ""
                                if "Author: " in para.additional_context:
                                    author = para.additional_context.split("Author: ")[
                                        1
                                    ].split(",")[0]
                                    author = f" (by {author})"

                                result.append(
                                    f"**Comment {comment_id}{author}**: {para.raw_text}"
                                )
                                result.append("")
                    else:
                        # For object mode, just add comments as paragraphs
                        result.extend(comment_paragraphs)
                except Exception as e:
                    if strict_mode:
                        # In strict mode, re-raise as DocxContentError
                        raise DocxContentError(
                            f"Error processing comments: {str(e)}"
                        ) from e
                    # Log error and continue without comments
                    logger.warning(f"Error processing comments: {str(e)}")

            # Process footers
            if include_footers and package.footers:
                try:
                    footer_paragraphs = self._process_footers(
                        package,
                        strict_mode=strict_mode,
                        include_textboxes=include_textboxes,
                    )
                    if markdown_mode and footer_paragraphs:
                        for para in footer_paragraphs:
                            # Add clear Footer marker
                            result.append(f"**Footer**: {para.raw_text}")
                            result.append("")
                    else:
                        # For object mode, add footers at the end
                        result.extend(footer_paragraphs)
                except Exception as e:
                    if strict_mode:
                        # In strict mode, re-raise as DocxContentError
                        raise DocxContentError(
                            f"Error processing footers: {str(e)}"
                        ) from e
                    # Log error and continue without footers
                    logger.warning(f"Error processing footers: {str(e)}")

            return result
        except DocxConverterError:
            # Re-raise specific converter errors
            raise
        except Exception as e:
            # Handle general errors in document processing
            raise DocxXmlError(f"Error processing document elements: {str(e)}") from e

    def _extract_images(
        self, package: _DocxPackage, strict_mode: bool = False
    ) -> list[Image]:
        """
        Extracts images from the DOCX document.

        :param package: _DocxPackage object
        :param strict_mode: If True, raise exceptions for any processing error
            instead of skipping problematic elements (default: False)
        :return: List of Image objects
        """
        images = []
        img_count = 0
        error_count = 0

        try:
            logger.debug(
                f"Extracting images from DOCX (found {len(package.images)} images)"
            )
            for rel_id, image_info in package.images.items():
                # Get image data and mime type
                image_bytes = image_info["data"]
                mime_type = image_info["mime_type"]

                # Ensure mime type is supported
                if mime_type not in {
                    "image/jpg",
                    "image/jpeg",
                    "image/png",
                    "image/webp",
                }:
                    # Default to PNG if unsupported
                    logger.debug(
                        f"Unsupported image MIME type: {mime_type}, defaulting to image/png"
                    )
                    mime_type = "image/png"

                try:
                    # Convert to base64
                    b64_data = base64.b64encode(image_bytes).decode("utf-8")
                    img_instance = Image(base64_data=b64_data, mime_type=mime_type)
                    images.append(img_instance)
                    img_count += 1
                except Exception as e:
                    # If in strict mode, raise the error
                    if strict_mode:
                        raise DocxContentError(
                            f"Error converting image '{image_info.get('target', rel_id)}': {str(e)}"
                        ) from e

                    # Otherwise log the error and continue with the next image
                    error_count += 1
                    logger.warning(
                        f"Error converting image '{image_info.get('target', rel_id)}': {str(e)}"
                    )
                    continue

            if img_count > 0:
                logger.info(f"Successfully extracted {img_count} images from DOCX")
            if error_count > 0:
                logger.warning(f"Failed to extract {error_count} images from DOCX")

            return images
        except Exception as e:
            # Handle critical errors extracting images
            raise DocxConverterError(
                f"Error extracting images from DOCX: {str(e)}"
            ) from e
