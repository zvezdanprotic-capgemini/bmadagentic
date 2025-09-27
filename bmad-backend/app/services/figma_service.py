import FigmaPy
import requests
from app.models import ManagedDocument
from typing import List, Optional

class FigmaService:
    """Figma API integration for design components and user flows."""
    
    def __init__(self, token: str = None):
        self.token = token
        self.figma_py = None
        if token:
            self.figma_py = FigmaPy.FigmaPy(token=token)
        
    def set_token(self, token: str):
        """Set or update the Figma API token."""
        self.token = token
        self.figma_py = FigmaPy.FigmaPy(token=token)
        
    def get_file_components(self, file_id: str, session_id: str) -> List[ManagedDocument]:
        """Get components from a Figma file."""
        if not self.figma_py:
            return []
            
        try:
            # Get file data using FigmaPy
            file_data = self.figma_py.get_file(file_id)
            
            if not file_data:
                return []
            
            # Extract components from the file
            components = []
            document = file_data.document if hasattr(file_data, 'document') else {}
            
            def extract_components(node, parent_name=""):
                """Recursively extract components from Figma nodes."""
                if not isinstance(node, dict):
                    return
                    
                node_type = node.get('type', '')
                node_name = node.get('name', 'Unnamed')
                
                # If this is a component, add it to our list
                if node_type == 'COMPONENT':
                    components.append({
                        'id': node.get('id'),
                        'name': node_name,
                        'type': node_type,
                        'parent': parent_name,
                        'description': node.get('description', ''),
                        'componentSetId': node.get('componentSetId'),
                        'absoluteBoundingBox': node.get('absoluteBoundingBox', {}),
                        'constraints': node.get('constraints', {}),
                        'styles': node.get('styles', {})
                    })
                
                # Process children
                children = node.get('children', [])
                for child in children:
                    extract_components(child, node_name)
            
            # Start extraction from document root
            extract_components(document)
            
            # Create managed document for this file
            file_name = getattr(file_data, 'name', f'Figma File {file_id}')
            doc = ManagedDocument(
                name=f"{file_name} - Components",
                type="figma_components",
                source=f"figma://file/{file_id}",
                external_url=f"https://www.figma.com/file/{file_id}",
                metadata={
                    "content": {
                        "file_id": file_id,
                        "file_name": file_name,
                        "components": components,
                        "total_components": len(components),
                        "session_id": session_id
                    },
                    "file_key": file_id,
                    "last_modified": getattr(file_data, 'last_modified', None),
                    "version": getattr(file_data, 'schema_version', None),
                    "thumbnail_url": getattr(file_data, 'thumbnail_url', None)
                }
            )
            
            return [doc]
            
        except Exception as e:
            return {
                "error": f"Error fetching Figma components: {str(e)}",
                "components": []
            }

    def get_user_flow_diagram(self, file_id: str, session_id: str) -> List[ManagedDocument]:
        """Get user flows from a Figma file."""
        if not self.figma_py:
            return []
            
        try:
            # Get file data using FigmaPy
            file_data = self.figma_py.get_file(file_id)
            
            if not file_data:
                return []
            
            # Extract flows and screens from the file
            user_flows = []
            screens = []
            document = file_data.document if hasattr(file_data, 'document') else {}
            
            def extract_flows_and_screens(node, parent_name=""):
                """Recursively extract flow-related elements from Figma nodes."""
                if not isinstance(node, dict):
                    return
                    
                node_type = node.get('type', '')
                node_name = node.get('name', 'Unnamed')
                
                # Look for frames that might represent screens or flows
                if node_type == 'FRAME':
                    # Check if this looks like a screen or flow diagram
                    if any(keyword in node_name.lower() for keyword in ['screen', 'page', 'flow', 'wireframe', 'mockup']):
                        screens.append({
                            'id': node.get('id'),
                            'name': node_name,
                            'type': 'screen',
                            'parent': parent_name,
                            'absoluteBoundingBox': node.get('absoluteBoundingBox', {}),
                            'background': node.get('background', []),
                            'effects': node.get('effects', [])
                        })
                
                # Look for connectors or arrows that might represent flow
                elif node_type == 'LINE' or (node_type == 'VECTOR' and 'arrow' in node_name.lower()):
                    user_flows.append({
                        'id': node.get('id'),
                        'name': node_name,
                        'type': 'connector',
                        'parent': parent_name,
                        'absoluteBoundingBox': node.get('absoluteBoundingBox', {}),
                        'strokes': node.get('strokes', [])
                    })
                
                # Process children
                children = node.get('children', [])
                for child in children:
                    extract_flows_and_screens(child, node_name)
            
            # Start extraction from document root
            extract_flows_and_screens(document)
            
            # Try to get file images for visual representation
            try:
                file_images = self.figma_py.get_file_images(file_id, format="png", scale=1)
                image_urls = file_images.get('images', {}) if file_images else {}
            except:
                image_urls = {}
            
            # Create managed document for this flow
            file_name = getattr(file_data, 'name', f'Figma File {file_id}')
            doc = ManagedDocument(
                name=f"{file_name} - User Flows",
                type="figma_user_flows",
                source=f"figma://file/{file_id}",
                external_url=f"https://www.figma.com/file/{file_id}",
                metadata={
                    "content": {
                        "file_id": file_id,
                        "file_name": file_name,
                        "screens": screens,
                        "flows": user_flows,
                        "image_urls": image_urls,
                        "total_screens": len(screens),
                        "total_flows": len(user_flows),
                        "session_id": session_id
                    },
                    "file_key": file_id,
                    "last_modified": getattr(file_data, 'last_modified', None),
                    "version": getattr(file_data, 'schema_version', None),
                    "thumbnail_url": getattr(file_data, 'thumbnail_url', None)
                }
            )
            
            return [doc]
            
        except Exception as e:
            return []
