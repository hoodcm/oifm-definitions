#!/usr/bin/env python3
"""
Batch creation script for Harrison.ai CXR findings OIFM codes.

Creates OIFM codes for all 241 findings in harrison_findings.json with
category-specific attributes and constrained selection options.
"""

import json
import re
from pathlib import Path
from typing import Any

from findingmodel.finding_model import (
    ChoiceAttribute,
    ChoiceValue,
    FindingModelBase,
    FindingModelFull,
)
from findingmodel.index import DuckDBIndex

# =============================================================================
# Standard Attribute Templates
# =============================================================================

PRESENCE_ATTRIBUTE = ChoiceAttribute(
    name="presence",
    description="Whether the finding is present on the imaging study",
    type="choice",
    values=[
        ChoiceValue(name="absent", description="Finding is not present"),
        ChoiceValue(name="present", description="Finding is present"),
        ChoiceValue(name="indeterminate", description="Cannot determine if finding is present"),
    ],
    required=True,
    max_selected=1,
)

CHANGE_FROM_PRIOR_ATTRIBUTE = ChoiceAttribute(
    name="change from prior",
    description="Change in the finding compared to prior imaging",
    type="choice",
    values=[
        ChoiceValue(name="new", description="Finding is new since prior study"),
        ChoiceValue(name="unchanged", description="Finding is unchanged from prior study"),
        ChoiceValue(name="increased", description="Finding has increased since prior study"),
        ChoiceValue(name="decreased", description="Finding has decreased since prior study"),
        ChoiceValue(name="resolved", description="Finding has resolved since prior study"),
    ],
    required=False,
    max_selected=1,
)

LATERALITY_ATTRIBUTE = ChoiceAttribute(
    name="laterality",
    description="Side of the body where the finding is located",
    type="choice",
    values=[
        ChoiceValue(name="left", description="Left side"),
        ChoiceValue(name="right", description="Right side"),
        ChoiceValue(name="bilateral", description="Both sides"),
    ],
    required=False,
    max_selected=1,
)

# =============================================================================
# Category-Specific Attribute Templates
# =============================================================================

# Bones - Chronicity (for fractures)
CHRONICITY_ATTRIBUTE = ChoiceAttribute(
    name="chronicity",
    description="Temporal stage of the finding",
    type="choice",
    values=[
        ChoiceValue(name="acute", description="Recent or new finding"),
        ChoiceValue(name="subacute", description="Intermediate stage"),
        ChoiceValue(name="chronic", description="Long-standing finding"),
        ChoiceValue(name="indeterminate", description="Age cannot be determined"),
    ],
    required=False,
    max_selected=1,
)

# Lines/Tubes/Devices - Position
POSITION_ATTRIBUTE = ChoiceAttribute(
    name="position",
    description="Position status of the device or tube",
    type="choice",
    values=[
        ChoiceValue(name="in position", description="Device is in expected/correct position"),
        ChoiceValue(name="suboptimal", description="Device position is suboptimal but functional"),
        ChoiceValue(name="malpositioned", description="Device is malpositioned and may require adjustment"),
    ],
    required=False,
    max_selected=1,
)

# Lungs - Distribution
DISTRIBUTION_ATTRIBUTE = ChoiceAttribute(
    name="distribution",
    description="Spatial distribution pattern of the finding",
    type="choice",
    values=[
        ChoiceValue(name="focal", description="Localized to a single area"),
        ChoiceValue(name="multifocal", description="Multiple discrete areas"),
        ChoiceValue(name="diffuse", description="Widespread throughout"),
        ChoiceValue(name="lobar", description="Confined to a lobe"),
        ChoiceValue(name="segmental", description="Confined to a segment"),
    ],
    required=False,
    max_selected=1,
)

# Lungs - Location Zone
LOCATION_ZONE_ATTRIBUTE = ChoiceAttribute(
    name="location zone",
    description="Vertical zone location in the lung",
    type="choice",
    values=[
        ChoiceValue(name="upper", description="Upper lung zone"),
        ChoiceValue(name="mid", description="Mid lung zone"),
        ChoiceValue(name="lower", description="Lower lung zone"),
        ChoiceValue(name="all zones", description="All lung zones"),
        ChoiceValue(name="perihilar", description="Central/perihilar region"),
    ],
    required=False,
    max_selected=1,
)

# Pleura - Size
SIZE_ATTRIBUTE = ChoiceAttribute(
    name="size",
    description="Size or extent of the finding",
    type="choice",
    values=[
        ChoiceValue(name="small", description="Small size or minimal extent"),
        ChoiceValue(name="moderate", description="Moderate size or extent"),
        ChoiceValue(name="large", description="Large size or extensive"),
    ],
    required=False,
    max_selected=1,
)

# Chest Walls / Technical - Severity
SEVERITY_ATTRIBUTE = ChoiceAttribute(
    name="severity",
    description="Severity or degree of the finding",
    type="choice",
    values=[
        ChoiceValue(name="mild", description="Mild degree"),
        ChoiceValue(name="moderate", description="Moderate degree"),
        ChoiceValue(name="severe", description="Severe degree"),
    ],
    required=False,
    max_selected=1,
)

# =============================================================================
# Grading Rubric Attributes (apply to ALL findings for concordance scoring)
# =============================================================================

# Temporality - when did the finding occur/appear
TEMPORALITY_ATTRIBUTE = ChoiceAttribute(
    name="temporality",
    description="Timing or onset of the finding relative to clinical context",
    type="choice",
    values=[
        ChoiceValue(name="acute", description="Recent onset, typically hours to days"),
        ChoiceValue(name="subacute", description="Intermediate duration, typically days to weeks"),
        ChoiceValue(name="chronic", description="Long-standing, typically weeks to months or longer"),
        ChoiceValue(name="indeterminate", description="Timing cannot be determined from imaging"),
        ChoiceValue(name="not applicable", description="Temporality not relevant for this finding"),
    ],
    required=False,
    max_selected=1,
)

# Stability - change over time (different from "change from prior" which compares studies)
STABILITY_ATTRIBUTE = ChoiceAttribute(
    name="stability",
    description="Stability status of the finding over time",
    type="choice",
    values=[
        ChoiceValue(name="stable", description="Finding has remained unchanged"),
        ChoiceValue(name="improving", description="Finding is getting better"),
        ChoiceValue(name="worsening", description="Finding is getting worse"),
        ChoiceValue(name="indeterminate", description="Stability cannot be determined"),
        ChoiceValue(name="not applicable", description="No prior study for comparison"),
    ],
    required=False,
    max_selected=1,
)

# Criticality - clinical urgency level
CRITICALITY_ATTRIBUTE = ChoiceAttribute(
    name="criticality",
    description="Clinical urgency or importance of the finding",
    type="choice",
    values=[
        ChoiceValue(name="critical", description="Requires immediate attention or action"),
        ChoiceValue(name="urgent", description="Requires attention within hours"),
        ChoiceValue(name="routine", description="Requires standard follow-up"),
        ChoiceValue(name="incidental", description="Noted but no specific action required"),
    ],
    required=False,
    max_selected=1,
)

# Actionable - whether finding requires clinical action
ACTIONABLE_ATTRIBUTE = ChoiceAttribute(
    name="actionable",
    description="Whether the finding requires clinical action or follow-up",
    type="choice",
    values=[
        ChoiceValue(name="actionable", description="Finding requires specific clinical action"),
        ChoiceValue(name="potentially actionable", description="May require action depending on clinical context"),
        ChoiceValue(name="non-actionable", description="No specific action required"),
    ],
    required=False,
    max_selected=1,
)


# =============================================================================
# Category Configuration
# =============================================================================

def get_category_attributes(category: str, finding_name: str) -> list[ChoiceAttribute]:
    """Get the default attributes for a category, customized by finding name."""
    category_lower = category.lower()
    finding_lower = finding_name.lower()

    # Always start with presence and change_from_prior
    attrs = [PRESENCE_ATTRIBUTE, CHANGE_FROM_PRIOR_ATTRIBUTE]

    # =========================================================================
    # Category-specific attributes
    # =========================================================================

    if category_lower == "abdomen":
        # Abdomen findings - add size for most
        attrs.append(SIZE_ATTRIBUTE)

    elif category_lower == "bones":
        # Add laterality for most bone findings
        if any(kw in finding_lower for kw in ["fracture", "lesion", "dislocation", "arthritis"]):
            attrs.append(LATERALITY_ATTRIBUTE)
        # Add chronicity for fractures
        if "fracture" in finding_lower:
            attrs.append(CHRONICITY_ATTRIBUTE)
        # Add severity for degenerative changes
        if any(kw in finding_lower for kw in ["degenerative", "arthritis", "osteopenia"]):
            attrs.append(SEVERITY_ATTRIBUTE)

    elif category_lower == "chest walls":
        # Add laterality where applicable
        if any(kw in finding_lower for kw in ["mastectomy", "breast", "axillary", "hemidiaphragm"]):
            attrs.append(LATERALITY_ATTRIBUTE)
        # Add severity for effusions, enlargement
        if any(kw in finding_lower for kw in ["effusion", "enlargement", "enlarged", "dilated"]):
            attrs.append(SEVERITY_ATTRIBUTE)
        # Add size for masses and effusions
        if any(kw in finding_lower for kw in ["mass", "effusion", "collection"]):
            attrs.append(SIZE_ATTRIBUTE)

    elif category_lower == "lines, tubes, devices":
        # Add position for tubes and catheters
        if any(kw in finding_lower for kw in ["tube", "catheter", "line", "drain"]):
            attrs.append(POSITION_ATTRIBUTE)
        # Add laterality for some devices
        if any(kw in finding_lower for kw in ["catheter", "drain", "picc", "central"]):
            attrs.append(LATERALITY_ATTRIBUTE)

    elif category_lower == "lungs":
        attrs.append(LATERALITY_ATTRIBUTE)
        # Add distribution for opacities and parenchymal findings
        if any(kw in finding_lower for kw in ["opacity", "consolidation", "atelectasis", "edema",
                                               "fibrosis", "nodule", "mass", "infiltrate"]):
            attrs.append(DISTRIBUTION_ATTRIBUTE)
            attrs.append(LOCATION_ZONE_ATTRIBUTE)
        # Add size for discrete findings
        if any(kw in finding_lower for kw in ["nodule", "mass", "opacity", "consolidation"]):
            attrs.append(SIZE_ATTRIBUTE)
        # Add severity for diffuse processes
        if any(kw in finding_lower for kw in ["edema", "fibrosis", "emphysema", "hyperinflation"]):
            attrs.append(SEVERITY_ATTRIBUTE)

    elif category_lower == "pleura":
        attrs.append(LATERALITY_ATTRIBUTE)
        # Add size for effusions and pneumothorax
        if any(kw in finding_lower for kw in ["effusion", "pneumothorax", "thickening"]):
            attrs.append(SIZE_ATTRIBUTE)

    elif category_lower == "technical factors":
        # Add severity for technical issues
        attrs.append(SEVERITY_ATTRIBUTE)

    # =========================================================================
    # Grading rubric attributes (apply to ALL findings for concordance scoring)
    # These are the columns from Bernardo's spreadsheet that need constrained choices
    # =========================================================================
    attrs.append(TEMPORALITY_ATTRIBUTE)
    attrs.append(STABILITY_ATTRIBUTE)
    attrs.append(CRITICALITY_ATTRIBUTE)
    attrs.append(ACTIONABLE_ATTRIBUTE)

    return attrs


def parse_comma_values(value_str: str | None) -> list[str]:
    """Parse comma-separated values into a list."""
    if not value_str:
        return []
    # Split by comma, strip whitespace, filter empty
    values = [v.strip() for v in value_str.split(",")]
    return [v for v in values if v]


def create_custom_attribute(name: str, values: list[str], description: str = "") -> ChoiceAttribute:
    """Create a custom choice attribute from a list of value strings."""
    # Ensure at least 2 values (OIFM requirement)
    if len(values) < 2:
        values = values + ["other"]  # Add "other" if only one value

    choice_values = [ChoiceValue(name=v) for v in values]

    return ChoiceAttribute(
        name=name,
        description=description or f"Specific {name} for this finding",
        type="choice",
        values=choice_values,
        required=False,
        max_selected=1,
    )


def generate_description(finding_name: str, category: str) -> str:
    """Generate a description for a finding based on name and category."""
    # Capitalize first letter of finding name
    name_cap = finding_name[0].upper() + finding_name[1:] if finding_name else finding_name

    category_context = {
        "Abdomen": "abdominal",
        "Bones": "skeletal/osseous",
        "Chest Walls": "chest wall or mediastinal",
        "Chest walls": "chest wall or mediastinal",
        "Lines, Tubes, Devices": "support device",
        "Lungs": "pulmonary",
        "Pleura": "pleural",
        "Technical Factors": "image quality",
    }

    context = category_context.get(category, "radiographic")
    return f"{name_cap} - a {context} finding observed on chest X-ray."


def normalize_finding_name(name: str) -> str:
    """Normalize finding name for use as filename."""
    # Replace special characters with underscores
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", name.lower())
    # Remove leading/trailing underscores
    normalized = normalized.strip("_")
    # Limit length
    return normalized[:60]


def create_finding_model(
    finding: dict[str, Any],
    index: DuckDBIndex,
) -> tuple[FindingModelFull, dict[str, str]]:
    """
    Create a FindingModelFull for a single Harrison finding.

    Returns:
        Tuple of (FindingModelFull, crosswalk_entry)
    """
    name = finding["finding"]
    category = finding["category"]

    # Get base attributes for this category
    attributes = get_category_attributes(category, name)

    # Add custom attributes from the finding's column values
    if finding.get("characteristics"):
        values = parse_comma_values(finding["characteristics"])
        if values:
            attrs = create_custom_attribute(
                "characteristics",
                values,
                f"Specific characteristics of {name}",
            )
            attributes.append(attrs)

    if finding.get("chronicity") and "chronicity" not in [a.name for a in attributes]:
        values = parse_comma_values(finding["chronicity"])
        if values:
            attrs = create_custom_attribute("chronicity", values, "Temporal stage")
            attributes.append(attrs)

    if finding.get("location"):
        values = parse_comma_values(finding["location"])
        if values:
            attrs = create_custom_attribute("location", values, f"Location of {name}")
            attributes.append(attrs)

    if finding.get("stability"):
        values = parse_comma_values(finding["stability"])
        if values:
            attrs = create_custom_attribute("stability", values, "Stability status")
            attributes.append(attrs)

    # Create the base model
    description = generate_description(name, category)

    base_model = FindingModelBase(
        name=name,
        description=description,
        synonyms=None,
        tags=[category.lower().replace(" ", "_"), "cxr", "harrison_ai"],
        attributes=attributes,
    )

    # Add OIFM IDs
    full_model = index.add_ids_to_model(base_model, "MGB")

    # Create crosswalk entry
    crosswalk = {
        "finding_name": name,
        "oifm_id": full_model.oifm_id,
        "category": category,
    }

    return full_model, crosswalk


def main():
    """Main entry point for batch OIFM creation."""
    # Paths
    base_dir = Path(__file__).parent.parent
    input_file = base_dir / "harrison_findings.json"
    output_dir = base_dir / "harrison_oifm_defs"
    crosswalk_file = base_dir / "harrison_oifm_crosswalk.json"

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    # Load input data
    print(f"Loading findings from {input_file}...")
    with open(input_file) as f:
        findings = json.load(f)

    print(f"Found {len(findings)} findings to process")

    # Initialize index
    print("Initializing DuckDB index...")
    index = DuckDBIndex(read_only=False)

    # Process each finding
    crosswalk_entries = []
    updated_findings = []

    for i, finding in enumerate(findings):
        name = finding["finding"]
        print(f"[{i+1}/{len(findings)}] Processing: {name}")

        try:
            full_model, crosswalk = create_finding_model(finding, index)

            # Save individual .fm.json file
            filename = normalize_finding_name(name) + ".fm.json"
            output_path = output_dir / filename
            with open(output_path, "w") as f:
                f.write(full_model.model_dump_json(indent=2, exclude_none=True))

            # Update the finding with the OIFM code
            updated_finding = finding.copy()
            updated_finding["cde_codes"] = full_model.oifm_id
            updated_findings.append(updated_finding)

            crosswalk_entries.append(crosswalk)

        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            updated_findings.append(finding)  # Keep original if error

    # Save crosswalk
    print(f"\nSaving crosswalk to {crosswalk_file}...")
    with open(crosswalk_file, "w") as f:
        json.dump(crosswalk_entries, f, indent=2)

    # Update the original findings file
    print(f"Updating {input_file} with OIFM codes...")
    with open(input_file, "w") as f:
        json.dump(updated_findings, f, indent=2)

    # Summary
    success_count = len([e for e in crosswalk_entries])
    print(f"\n{'='*60}")
    print(f"COMPLETE: {success_count}/{len(findings)} findings processed")
    print(f"Output files: {output_dir}")
    print(f"Crosswalk: {crosswalk_file}")
    print(f"Updated: {input_file}")


if __name__ == "__main__":
    main()
