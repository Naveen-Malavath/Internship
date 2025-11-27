"""
Test script to verify DBD (Database Design) diagram generation fixes.

This script tests the improved brace counting logic and field removal safety checks.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.services.agent3 import Agent3Service

# Configure logging to see debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_dbd_generation():
    """Test DBD diagram generation with sample e-commerce features."""
    
    # Check if API key is available
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("❌ ANTHROPIC_API_KEY not found in environment")
        logger.error("Please set your API key: export ANTHROPIC_API_KEY='your-key-here'")
        return
    
    logger.info("=" * 80)
    logger.info("🧪 Testing DBD (Database Design) Diagram Generation")
    logger.info("=" * 80)
    
    # Initialize Agent3Service
    agent3 = Agent3Service()
    
    # Sample features for an e-commerce project
    features = [
        {
            "feature_text": "User Authentication: Allow users to register, login, and manage their accounts with secure password handling",
            "title": "User Authentication",
            "feature_id": "1"
        },
        {
            "feature_text": "Product Catalog: Display products with details, images, prices, and stock availability organized by categories",
            "title": "Product Catalog",
            "feature_id": "2"
        },
        {
            "feature_text": "Shopping Cart: Enable users to add/remove products, update quantities, and view cart totals",
            "title": "Shopping Cart",
            "feature_id": "3"
        },
        {
            "feature_text": "Order Management: Process customer orders, track order status, and generate order confirmations",
            "title": "Order Management",
            "feature_id": "4"
        },
        {
            "feature_text": "Payment Processing: Integrate payment gateway to handle secure transactions with multiple payment methods",
            "title": "Payment Processing",
            "feature_id": "5"
        }
    ]
    
    # Sample stories
    stories = [
        {
            "story_text": "As a customer, I want to create an account so that I can track my orders",
            "feature_id": "1"
        },
        {
            "story_text": "As a customer, I want to browse products by category so that I can find what I need",
            "feature_id": "2"
        },
        {
            "story_text": "As a customer, I want to add products to my cart so that I can purchase multiple items",
            "feature_id": "3"
        },
        {
            "story_text": "As a customer, I want to checkout and place an order so that I can receive my products",
            "feature_id": "4"
        },
        {
            "story_text": "As a customer, I want to pay securely so that my financial information is protected",
            "feature_id": "5"
        }
    ]
    
    # Test parameters
    project_title = "E-Commerce Platform"
    original_prompt = "Build a full-featured e-commerce platform for online retail"
    
    logger.info(f"\n📝 Project: {project_title}")
    logger.info(f"📝 Features: {len(features)}")
    logger.info(f"📝 Stories: {len(stories)}")
    logger.info("\n" + "=" * 80)
    logger.info("🚀 Generating DBD diagram...")
    logger.info("=" * 80 + "\n")
    
    try:
        # Generate DBD diagram
        mermaid_code = await agent3.generate_mermaid(
            project_title=project_title,
            features=features,
            stories=stories,
            diagram_type="database",  # This will trigger DBD generation
            original_prompt=original_prompt
        )
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ DBD DIAGRAM GENERATED SUCCESSFULLY")
        logger.info("=" * 80)
        
        # Save to file
        output_file = Path(__file__).parent / "test_dbd_fixed_output.mmd"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(mermaid_code)
        
        logger.info(f"\n💾 Diagram saved to: {output_file}")
        
        # Analyze the output
        logger.info("\n" + "=" * 80)
        logger.info("📊 OUTPUT ANALYSIS")
        logger.info("=" * 80)
        
        lines = mermaid_code.split('\n')
        
        # Count entities and fields
        entities = []
        entity_fields = {}
        relationships = []
        
        current_entity = None
        for line in lines:
            stripped = line.strip()
            
            # Check for entity definition
            import re
            entity_match = re.match(r'^([A-Z_][A-Z_0-9]*)\s*\{', stripped)
            if entity_match:
                entity_name = entity_match.group(1)
                entities.append(entity_name)
                current_entity = entity_name
                entity_fields[entity_name] = []
                continue
            
            # Check for closing brace
            if stripped == '}':
                current_entity = None
                continue
            
            # Check for field definition
            if current_entity and re.match(r'^\s*(uuid|varchar|text|int|float|boolean|datetime|timestamp|json)', stripped):
                entity_fields[current_entity].append(stripped)
            
            # Check for relationship
            if '||--' in stripped or '}o--' in stripped or 'o{--' in stripped:
                relationships.append(stripped)
        
        logger.info(f"\n📈 Statistics:")
        logger.info(f"   - Total entities: {len(entities)}")
        logger.info(f"   - Total relationships: {len(relationships)}")
        
        # Check for empty entities
        empty_entities = [name for name, fields in entity_fields.items() if len(fields) == 0]
        entities_with_fields = [name for name, fields in entity_fields.items() if len(fields) > 0]
        
        if empty_entities:
            logger.error(f"\n❌ EMPTY ENTITIES DETECTED ({len(empty_entities)}):")
            for entity in empty_entities:
                logger.error(f"   - {entity} (0 fields)")
            logger.error("\n⚠️ This indicates the fix may not be working correctly!")
        else:
            logger.info(f"\n✅ All entities have fields!")
        
        if entities_with_fields:
            logger.info(f"\n✅ ENTITIES WITH FIELDS ({len(entities_with_fields)}):")
            for entity in entities_with_fields:
                field_count = len(entity_fields[entity])
                logger.info(f"   - {entity}: {field_count} fields")
                # Show first 3 fields as sample
                for field in entity_fields[entity][:3]:
                    logger.info(f"      • {field}")
                if field_count > 3:
                    logger.info(f"      ... and {field_count - 3} more")
        
        # Show relationships
        if relationships:
            logger.info(f"\n🔗 RELATIONSHIPS ({len(relationships)}):")
            for rel in relationships[:5]:  # Show first 5
                logger.info(f"   - {rel}")
            if len(relationships) > 5:
                logger.info(f"   ... and {len(relationships) - 5} more")
        
        # Overall verdict
        logger.info("\n" + "=" * 80)
        if empty_entities:
            logger.error("❌ TEST RESULT: FAILED - Empty entities detected")
            logger.error("   The brace counting fix may need further adjustment")
        else:
            logger.info("✅ TEST RESULT: PASSED - All entities have proper fields")
            logger.info("   The DBD generation is working correctly!")
        logger.info("=" * 80)
        
        # Show preview of diagram
        logger.info(f"\n📄 DIAGRAM PREVIEW (first 30 lines):")
        logger.info("-" * 80)
        for i, line in enumerate(lines[:30], 1):
            logger.info(f"{i:3d}| {line}")
        if len(lines) > 30:
            logger.info(f"... ({len(lines) - 30} more lines)")
        logger.info("-" * 80)
        
    except Exception as e:
        logger.error(f"\n❌ ERROR during DBD generation: {e}", exc_info=True)
        logger.error("\n" + "=" * 80)
        logger.error("❌ TEST RESULT: FAILED - Exception occurred")
        logger.error("=" * 80)


async def test_hospital_management():
    """Test DBD generation with hospital management features."""
    
    logger.info("\n\n" + "=" * 80)
    logger.info("🧪 Testing DBD with Hospital Management System")
    logger.info("=" * 80)
    
    agent3 = Agent3Service()
    
    features = [
        {
            "feature_text": "Patient Registration: Register new patients with personal details, medical history, and insurance information",
            "title": "Patient Registration",
            "feature_id": "1"
        },
        {
            "feature_text": "Doctor Scheduling: Manage doctor schedules, availability, and appointments",
            "title": "Doctor Scheduling",
            "feature_id": "2"
        },
        {
            "feature_text": "Appointment Booking: Allow patients to book, reschedule, and cancel appointments",
            "title": "Appointment Booking",
            "feature_id": "3"
        },
        {
            "feature_text": "Medical Records: Store and manage patient medical records, diagnoses, and treatment history",
            "title": "Medical Records",
            "feature_id": "4"
        },
        {
            "feature_text": "Prescription Management: Generate, track, and manage patient prescriptions",
            "title": "Prescription Management",
            "feature_id": "5"
        }
    ]
    
    stories = [
        {"story_text": "As a receptionist, I want to register new patients quickly", "feature_id": "1"},
        {"story_text": "As a doctor, I want to manage my schedule and availability", "feature_id": "2"},
        {"story_text": "As a patient, I want to book appointments online", "feature_id": "3"},
        {"story_text": "As a doctor, I want to access patient medical history", "feature_id": "4"},
        {"story_text": "As a doctor, I want to create prescriptions for patients", "feature_id": "5"}
    ]
    
    try:
        mermaid_code = await agent3.generate_mermaid(
            project_title="Hospital Management System",
            features=features,
            stories=stories,
            diagram_type="database",
            original_prompt="Build a comprehensive hospital management system"
        )
        
        output_file = Path(__file__).parent / "test_dbd_hospital_output.mmd"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(mermaid_code)
        
        logger.info(f"✅ Hospital DBD saved to: {output_file}")
        
        # Quick analysis
        lines = mermaid_code.split('\n')
        import re
        entities = [line.strip().split()[0] for line in lines if re.match(r'^[A-Z_][A-Z_0-9]*\s*\{', line.strip())]
        logger.info(f"📊 Generated {len(entities)} entities: {', '.join(entities)}")
        
    except Exception as e:
        logger.error(f"❌ Hospital DBD test failed: {e}", exc_info=True)


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🔬 DBD (Database Design) Fix Verification Test")
    print("=" * 80)
    print("\nThis script will:")
    print("1. Generate a DBD diagram for an e-commerce project")
    print("2. Analyze the output for empty entities")
    print("3. Verify that the brace counting fix is working")
    print("\nMake sure you have:")
    print("- ANTHROPIC_API_KEY set in your environment")
    print("- Internet connection to call Claude API")
    print("\n" + "=" * 80 + "\n")
    
    # Run tests
    asyncio.run(test_dbd_generation())
    asyncio.run(test_hospital_management())
    
    print("\n" + "=" * 80)
    print("🏁 Test completed! Check the output above for results.")
    print("=" * 80 + "\n")

