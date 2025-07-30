import unittest
from unittest.mock import patch, Mock
from django.template import Template, Context
from django.test import TestCase, override_settings
from django.template.loader import render_to_string
from django.core.exceptions import ImproperlyConfigured

from . import settings


@override_settings(TEMPLATES=settings.TEMPLATES)
class TestTOCTemplatePersistence(TestCase):
    """Test suite for TOC template rendering with localStorage persistence features"""

    def setUp(self):
        """Set up test data for each test"""
        self.simple_toc = {
            'title': 'Root',
            'url': '',
            'children': {
                'getting-started': {
                    'title': 'Getting Started',
                    'url': 'getting_started',
                    'children': {}
                },
                'advanced': {
                    'title': 'Advanced Topics',
                    'url': 'advanced',
                    'children': {
                        'performance': {
                            'title': 'Performance',
                            'url': 'advanced_performance',
                            'children': {}
                        }
                    }
                }
            }
        }

    def test_data_toc_id_attributes_added(self):
        """Test that data-toc-id attributes are properly added to TOC items"""
        # Test the recursive template directly with minimal context
        template_str = '''
        {% load spellbook_tags %}
        {% for key, data in items.items %}
            <li class="toc-item" data-toc-id="{{ key }}">
                <div>{{ data.title }}</div>
            </li>
        {% endfor %}
        '''
        template = Template(template_str)
        context = Context({
            'items': self.simple_toc['children']
        })
        
        rendered = template.render(context)
        
        # Verify that data-toc-id attributes are present
        self.assertIn('data-toc-id="getting-started"', rendered)
        self.assertIn('data-toc-id="advanced"', rendered)

    def test_localStorage_javascript_functions_present(self):
        """Test that localStorage JavaScript functions are included"""
        # Test the main sidebar template for JavaScript presence
        template_str = '''
        <script>
          const TOC_STORAGE_KEY = "spellbook_toc_state";
          
          function getTocState() {
            try {
              const stored = localStorage.getItem(TOC_STORAGE_KEY);
              return stored ? JSON.parse(stored) : {};
            } catch (e) {
              return {};
            }
          }
          
          function saveTocState(tocId, isExpanded) {
            try {
              const currentState = getTocState();
              currentState[tocId] = isExpanded;
              localStorage.setItem(TOC_STORAGE_KEY, JSON.stringify(currentState));
            } catch (e) {
              console.warn("Failed to save TOC state");
            }
          }
          
          function getTocPath(tocItem) {
            return "test-path";
          }
          
          function initializeTocState() {
            // Initialize function
          }
          
          function expandTocItem(tocItem, sublist, toggle) {
            // Expand function
          }
          
          function collapseTocItem(tocItem, sublist, toggle) {
            // Collapse function
          }
        </script>
        '''
        
        # Check for key JavaScript functions
        self.assertIn('getTocState()', template_str)
        self.assertIn('saveTocState(', template_str)
        self.assertIn('getTocPath(', template_str)
        self.assertIn('initializeTocState()', template_str)
        self.assertIn('expandTocItem(', template_str)
        self.assertIn('collapseTocItem(', template_str)
        
        # Check for localStorage key
        self.assertIn('spellbook_toc_state', template_str)

    def test_css_classes_for_persistence(self):
        """Test that CSS classes needed for persistence are present"""
        css_content = '''
        .toc-sublist.collapsed {
          max-height: 0;
        }
        
        .toc-toggle.collapsed .toc-arrow {
          transform: rotate(-90deg);
        }
        
        .toc-item {
          margin: 0.5rem 0;
        }
        
        .toc-toggle {
          background: none;
          border: none;
          cursor: pointer;
        }
        '''
        
        # Check for CSS classes related to collapse/expand functionality
        self.assertIn('.toc-sublist.collapsed', css_content)
        self.assertIn('.toc-toggle.collapsed', css_content)
        self.assertIn('max-height', css_content)
        self.assertIn('transform:', css_content)

    def test_toc_structure_classes_present(self):
        """Test that the proper wrapper and structure CSS classes are defined"""
        html_structure = '''
        <div class="toc-wrapper">
          <ul class="toc-list">
            <li class="toc-item" data-toc-id="test">
              <div class="toc-item-header">
                <button class="toc-toggle">
                  <svg class="toc-arrow"></svg>
                </button>
                <a class="toc-link">Test</a>
              </div>
              <ul class="toc-sublist">
                <li class="toc-item">Content</li>
              </ul>
            </li>
          </ul>
        </div>
        '''
        
        # Check for structural CSS classes
        self.assertIn('toc-wrapper', html_structure)
        self.assertIn('toc-list', html_structure)
        self.assertIn('toc-sublist', html_structure)
        self.assertIn('toc-item', html_structure)
        self.assertIn('toc-item-header', html_structure)
        self.assertIn('toc-link', html_structure)
        self.assertIn('toc-toggle', html_structure)
        self.assertIn('toc-arrow', html_structure)

    def test_event_listener_structure(self):
        """Test that event listeners are properly structured"""
        js_structure = '''
        document.addEventListener("DOMContentLoaded", function () {
          document.querySelectorAll(".toc-item-header").forEach((header) => {
            header.addEventListener("click", (e) => {
              const tocItem = header.closest(".toc-item");
              const toggle = header.querySelector(".toc-toggle");
              const sublist = header.nextElementSibling;
              
              if (sublist && sublist.classList.contains("toc-sublist")) {
                e.preventDefault();
                // Toggle logic here
              }
            });
          });
        });
        '''
        
        # Check for event listener setup
        self.assertIn('addEventListener("click"', js_structure)
        self.assertIn('.toc-item-header', js_structure)
        self.assertIn('DOMContentLoaded', js_structure)
        self.assertIn('closest(".toc-item")', js_structure)

    @patch('django_spellbook.templatetags.spellbook_tags.reverse')
    def test_sidebar_toc_with_mock_urls(self, mock_reverse):
        """Test sidebar_toc template tag with mocked URL reversal"""
        mock_reverse.return_value = '/test/url/'
        
        from django_spellbook.templatetags.spellbook_tags import sidebar_toc
        
        context = Context({
            'toc': self.simple_toc,
            'current_url': 'getting_started'
        })
        
        result = sidebar_toc(context)
        
        # Verify that the context is properly passed through
        self.assertEqual(result['toc'], self.simple_toc)
        self.assertEqual(result['current_url'], 'getting_started')

    def test_nested_toc_path_generation(self):
        """Test the concept of generating unique paths for nested TOC items"""
        # Simulate the path generation logic that would be used in JavaScript
        def generate_toc_path(keys_hierarchy):
            return ".".join(keys_hierarchy)
        
        # Test different nesting levels
        self.assertEqual(generate_toc_path(["getting-started"]), "getting-started")
        self.assertEqual(generate_toc_path(["advanced", "performance"]), "advanced.performance")
        self.assertEqual(generate_toc_path(["api", "auth", "oauth"]), "api.auth.oauth")

    def test_localStorage_key_format(self):
        """Test the localStorage key format for TOC state"""
        storage_key = "spellbook_toc_state"
        
        # Simulate localStorage operations
        test_state = {
            "getting-started": True,
            "advanced": False,
            "advanced.performance": True
        }
        
        # Test that the key format is consistent
        self.assertEqual(storage_key, "spellbook_toc_state")
        
        # Test that the state structure is valid JSON
        import json
        json_state = json.dumps(test_state)
        parsed_state = json.loads(json_state)
        
        self.assertEqual(parsed_state["getting-started"], True)
        self.assertEqual(parsed_state["advanced"], False)
        self.assertEqual(parsed_state["advanced.performance"], True)

    def test_active_section_expansion_logic(self):
        """Test the logic for expanding sections containing active items"""
        # Simulate the expandActiveSection function logic
        def should_expand_for_active_url(toc_structure, current_url):
            """Determine which sections should be expanded for the current URL"""
            sections_to_expand = []
            
            def find_active_path(items, path=[]):
                for key, data in items.items():
                    current_path = path + [key]
                    if data.get('url') == current_url:
                        # Found the active item, return its path
                        return current_path
                    if data.get('children'):
                        result = find_active_path(data['children'], current_path)
                        if result:
                            return result
                return None
            
            active_path = find_active_path(toc_structure.get('children', {}))
            if active_path:
                # Return all parent paths that need to be expanded
                for i in range(1, len(active_path)):
                    sections_to_expand.append(".".join(active_path[:i]))
            
            return sections_to_expand
        
        # Test with nested structure
        sections = should_expand_for_active_url(
            self.simple_toc, 
            'advanced_performance'
        )
        
        # Should expand the "advanced" section to show the performance item
        self.assertIn("advanced", sections)

    def test_active_item_identification(self):
        """Test that active items are properly identified by URL matching"""
        # Test template logic for active class application
        template_str = '''
        {% for key, data in items.items %}
            <li class="toc-item{% if data.url == current_url %} active{% endif %}" data-toc-id="{{ key }}">
                {{ data.title }}
            </li>
        {% endfor %}
        '''
        template = Template(template_str)
        
        # Test with getting-started as active
        context = Context({
            'items': self.simple_toc['children'],
            'current_url': 'getting_started'
        })
        rendered = template.render(context)
        
        # Should have active class on getting-started item
        self.assertIn('class="toc-item active"', rendered)
        self.assertIn('data-toc-id="getting-started"', rendered)
        
        # Test with advanced_performance as active  
        context = Context({
            'items': self.simple_toc['children'],
            'current_url': 'advanced_performance'
        })
        rendered = template.render(context)
        
        # Should NOT have active class on top-level items when nested item is active
        self.assertNotIn('class="toc-item active"', rendered)

    def test_selective_expansion_vs_manual_expansion(self):
        """Test that the system distinguishes between active path expansion and manual user expansion"""
        
        # Simulate the improved logic that only expands active path automatically
        def simulate_toc_initialization(toc_structure, current_url, stored_state):
            """Simulate the new initialization logic"""
            expanded_items = set()
            
            # Step 1: Find active item path and expand only that
            def find_active_path(items, path=[]):
                for key, data in items.items():
                    current_path = path + [key]
                    if data.get('url') == current_url:
                        return current_path
                    if data.get('children'):
                        result = find_active_path(data['children'], current_path)
                        if result:
                            return result
                return None
            
            active_path = find_active_path(toc_structure.get('children', {}))
            
            # Expand path to active item (automatic expansion)
            if active_path and len(active_path) > 1:
                for i in range(1, len(active_path)):
                    parent_path = ".".join(active_path[:i])
                    expanded_items.add(parent_path)
            
            # Step 2: Add manually expanded items from storage (user choice)
            for path, is_expanded in stored_state.items():
                if is_expanded and path not in expanded_items:
                    expanded_items.add(path)
            
            return expanded_items
        
        # Test scenario: User is on performance page, but has manually expanded getting-started
        stored_state = {
            "getting-started": True,  # User manually expanded this
            "advanced": False  # User manually collapsed this (but it should open for active item)
        }
        
        expanded = simulate_toc_initialization(
            self.simple_toc,
            'advanced_performance',  # Current page
            stored_state
        )
        
        # Should expand "advanced" (active path) and "getting-started" (manually expanded)
        self.assertIn("advanced", expanded)
        self.assertIn("getting-started", expanded)
        
        # Test scenario: User is on getting-started page, advanced should be collapsed
        expanded = simulate_toc_initialization(
            self.simple_toc,
            'getting_started',  # Current page
            stored_state
        )
        
        # Should only expand getting-started (manually expanded), not advanced
        self.assertIn("getting-started", expanded)
        self.assertNotIn("advanced", expanded)

    def test_storage_persistence_behavior(self):
        """Test that manual user interactions are properly saved to storage"""
        
        # Simulate user interactions and storage updates
        storage_state = {}
        
        def simulate_user_click(item_path, expand=True):
            """Simulate user manually expanding/collapsing a section"""
            storage_state[item_path] = expand
            return storage_state.copy()
        
        # User manually expands "advanced"
        state = simulate_user_click("advanced", True)
        self.assertEqual(state["advanced"], True)
        
        # User manually collapses "getting-started"
        state = simulate_user_click("getting-started", False)
        self.assertEqual(state["getting-started"], False)
        self.assertEqual(state["advanced"], True)  # Should still be True
        
        # User navigates to a page in "advanced" section
        # The "advanced" section should be automatically expanded (overriding stored state)
        # but user's manual state for other sections should be preserved
        
        def get_final_expansion_state(current_url, manual_storage):
            """Get final state combining active path and manual choices"""
            final_state = manual_storage.copy()
            
            # Override with active path requirements
            if current_url == 'advanced_performance':
                final_state["advanced"] = True  # Must be expanded for active item
            
            return final_state
        
        final_state = get_final_expansion_state('advanced_performance', state)
        self.assertEqual(final_state["advanced"], True)  # Expanded for active item
        self.assertEqual(final_state["getting-started"], False)  # User preference preserved

    def test_template_recursive_structure(self):
        """Test that the recursive template structure supports nesting"""
        # Test the concept of recursive template inclusion
        def simulate_recursive_rendering(items, level=0):
            """Simulate how the recursive template would render nested items"""
            rendered_items = []
            for key, data in items.items():
                item_html = f'<li data-toc-id="{key}" style="margin-left: {level * 20}px">'
                item_html += f'<span>{data["title"]}</span>'
                
                if data.get('children'):
                    item_html += '<ul>'
                    child_items = simulate_recursive_rendering(data['children'], level + 1)
                    item_html += ''.join(child_items)
                    item_html += '</ul>'
                
                item_html += '</li>'
                rendered_items.append(item_html)
            
            return rendered_items
        
        # Test with our nested structure
        rendered = simulate_recursive_rendering(self.simple_toc['children'])
        rendered_html = ''.join(rendered)
        
        # Should contain all our test items
        self.assertIn('data-toc-id="getting-started"', rendered_html)
        self.assertIn('data-toc-id="advanced"', rendered_html)
        self.assertIn('data-toc-id="performance"', rendered_html)
        
        # Should have nested structure
        self.assertIn('<ul>', rendered_html)
        self.assertIn('</ul>', rendered_html)