#!/usr/bin/env python3
"""
Flask Validate Security Audit Script - Command Line Wrapper

This is a convenience wrapper to run the audit_security.py script from the project root.

Usage:
    python audit_security.py <flask_app>
    python audit_security.py tests/minimal_app.py:app
    python audit_security.py myapp:app
    python audit_security.py --help

This wrapper automatically finds and runs the audit script from the flask_request_validate package.
"""

import sys
import os

# Find the audit script in the package
script_dir = os.path.dirname(os.path.abspath(__file__))
audit_script = os.path.join(script_dir, 'src', 'flask_request_validate', 'audit_security.py')

# Import and run the main function
if __name__ == '__main__':
    # Execute the audit script with the same arguments
    exec(open(audit_script).read())#!/usr/bin/env python3
"""
Flask Validate Security Audit Script

This script analyzes Flask applications to identify unprotected entry points
that may accept user input without proper validation.

Usage:
    python audit_security.py <flask_app_module>
    python audit_security.py myapp:app
    python audit_security.py --help

Example:
    python audit_security.py tests.sample_app:app
"""

import sys
import os
import importlib
import inspect
from typing import Dict, List, Any, Optional


def import_flask_app(app_path: str):
    """
    Import a Flask application from a module path.

    :param app_path: Path like 'myapp:app' or 'myapp'
    :return: Flask app instance
    """
    if ':' in app_path:
        module_name, app_name = app_path.split(':', 1)
    else:
        module_name = app_path
        app_name = 'app'

    # Add current directory and project root to path
    current_dir = os.getcwd()
    sys.path.insert(0, current_dir)

    # Also add the parent directory in case we're in a subdirectory
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    try:
        module = importlib.import_module(module_name)
        app = getattr(module, app_name)
        return app
    except (ImportError, AttributeError) as e:
        print(f"❌ Error importing Flask app '{app_path}': {e}")
        print("Make sure the module is in your Python path and the app variable exists.")
        print(f"Current working directory: {current_dir}")
        print(f"Python path: {sys.path[:3]}...")  # Show first 3 entries
        sys.exit(1)


def analyze_route_security(app) -> Dict[str, Any]:
    """
    Analyze the security status of all routes in a Flask application.

    :param app: Flask application instance
    :return: Dictionary with security analysis results
    """
    protected_routes = set()
    excluded_routes = set()

    # Get all routes from the app and inspect their view functions
    all_routes = set()
    with app.app_context():
        for rule in app.url_map.iter_rules():
            if rule.endpoint == 'static':
                continue

            # Get the view function for this endpoint
            view_func = app.view_functions.get(rule.endpoint)
            if view_func:
                # Check if the function has validation decorators
                if hasattr(view_func, '__validation_protected__'):
                    # This route is protected
                    for method in rule.methods:
                        if method not in ('HEAD', 'OPTIONS'):
                            protected_routes.add(f"{method} {rule.rule}")
                elif hasattr(view_func, '__validation_excluded__'):
                    # This route is excluded
                    for method in rule.methods:
                        if method not in ('HEAD', 'OPTIONS'):
                            excluded_routes.add(f"{method} {rule.rule}")

            # Collect all routes
            for method in rule.methods:
                if method not in ('HEAD', 'OPTIONS'):
                    all_routes.add(f"{method} {rule.rule}")

    # Find routes that exist but aren't protected or excluded
    untracked_routes = all_routes - protected_routes - excluded_routes

    # Categorize untracked routes
    unprotected_routes = []
    for route in sorted(untracked_routes):
        method, path = route.split(' ', 1)

        # Prioritize routes that likely accept user input
        priority = 'low'
        if method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            priority = 'high'
        elif '<' in path:  # Routes with parameters
            priority = 'medium'

        unprotected_routes.append({
            'endpoint': route,
            'method': method,
            'path': path,
            'priority': priority,
            'likely_input_route': priority in ('high', 'medium')
        })

    return {
        'protected': sorted(protected_routes),
        'excluded': sorted(excluded_routes),
        'unprotected': unprotected_routes,
        'summary': {
            'total_routes': len(all_routes),
            'protected_count': len(protected_routes),
            'excluded_count': len(excluded_routes),
            'unprotected_count': len(unprotected_routes),
            'high_priority_unprotected': len([r for r in unprotected_routes if r['priority'] == 'high']),
            'medium_priority_unprotected': len([r for r in unprotected_routes if r['priority'] == 'medium']),
            'low_priority_unprotected': len([r for r in unprotected_routes if r['priority'] == 'low'])
        }
    }


def print_security_report(results: Dict[str, Any], verbose: bool = True):
    """
    Print a comprehensive security audit report.

    :param results: Security analysis results
    :param verbose: Whether to show detailed route lists
    """
    summary = results['summary']

    print("🔍 Flask Validate Security Audit Report")
    print("=" * 50)

    # Overall summary
    print("📊 OVERALL SUMMARY:")
    print(f"   Total routes analyzed: {summary['total_routes']}")
    print(f"   ✅ Protected routes: {summary['protected_count']}")
    print(f"   ⚪ Excluded routes: {summary['excluded_count']}")
    print(f"   ❌ Unprotected routes: {summary['unprotected_count']}")

    if summary['unprotected_count'] > 0:
        print(f"   🚨 High priority unprotected: {summary['high_priority_unprotected']}")
        print(f"   ⚠️  Medium priority unprotected: {summary['medium_priority_unprotected']}")
        print(f"   ℹ️  Low priority unprotected: {summary['low_priority_unprotected']}")

    # Security score
    protected_percentage = (summary['protected_count'] + summary['excluded_count']) / summary['total_routes'] * 100
    print(f"   🔒 Security Score: {protected_percentage:.1f}%")
    if protected_percentage >= 90:
        print("   🟢 Security Score: EXCELLENT")
    elif protected_percentage >= 75:
        print("   🟡 Security Score: GOOD")
    elif protected_percentage >= 50:
        print("   🟠 Security Score: FAIR")
    else:
        print("   🔴 Security Score: POOR")

    print()

    # Detailed reports
    if verbose:
        if results['protected']:
            print("✅ PROTECTED ROUTES (have @validate decorators):")
            for route in sorted(results['protected']):
                print(f"   ✓ {route}")
            print()

        if results['excluded']:
            print("⚪ EXCLUDED ROUTES (marked with @exclude_validation):")
            for route in sorted(results['excluded']):
                print(f"   ○ {route}")
            print()

        if results['unprotected']:
            print("❌ UNPROTECTED ROUTES (may need validation):")
            for route in results['unprotected']:
                priority_icon = {
                    'high': '🚨',
                    'medium': '⚠️ ',
                    'low': 'ℹ️ '
                }[route['priority']]
                print(f"   {priority_icon} {route['endpoint']} ({route['priority']} priority)")
            print()

    # Recommendations
    print("💡 RECOMMENDATIONS:")
    if summary['high_priority_unprotected'] > 0:
        print(f"   🚨 CRITICAL: {summary['high_priority_unprotected']} high-priority routes are unprotected!")
        print("      These routes accept user input (POST/PUT/PATCH/DELETE) and should be validated.")
        print("      Add @validate() decorators to these routes immediately.")

    if summary['medium_priority_unprotected'] > 0:
        print(f"   ⚠️  WARNING: {summary['medium_priority_unprotected']} routes with parameters may need validation.")
        print("      GET routes with parameters should be validated if they process user input.")

    if summary['unprotected_count'] == 0:
        print("   ✅ Excellent! All routes are properly protected or excluded.")
    else:
        print("   📝 For routes that genuinely don't need validation, use:")
        print("      @exclude_validation('reason why no validation needed')")
        print("      This will mark them as intentionally unprotected.")

    print()
    print("🔧 USAGE TIPS:")
    print("   • Run this audit regularly during development")
    print("   • Integrate into CI/CD pipelines for automated security checks")
    print("   • Use --fail-on-unprotected flag in CI for strict validation")
    print("   • Review excluded routes periodically to ensure they're still appropriate")


def main():
    """Main entry point for the audit script."""
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print(__doc__)
        sys.exit(0)

    app_path = sys.argv[1]

    # Import the Flask app
    print(f"🔍 Analyzing Flask app: {app_path}")
    app = import_flask_app(app_path)

    # Run security analysis
    print("🔒 Running security analysis...")
    results = analyze_route_security(app)

    # Print report
    print()
    print_security_report(results)

    # Exit with error code if there are high-priority unprotected routes
    if results['summary']['high_priority_unprotected'] > 0:
        print(f"\n❌ Audit failed: {results['summary']['high_priority_unprotected']} high-priority unprotected routes found!")
        sys.exit(1)
    else:
        print("\n✅ Audit passed: No high-priority security issues found.")
        sys.exit(0)


if __name__ == '__main__':
    main()