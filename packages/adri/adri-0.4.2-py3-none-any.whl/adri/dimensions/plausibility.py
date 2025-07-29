"""
Plausibility dimension assessment for the Agent Data Readiness Index.

This module evaluates whether data values are reasonable based on context,
and most importantly, whether this information is explicitly communicated to agents.
"""

import logging
from typing import Dict, List, Tuple, Any, Optional

from ..config.config import get_config
from ..connectors import BaseConnector
from . import BaseDimensionAssessor, register_dimension
from .business_plausibility import calculate_business_plausibility_score
from ..rules.registry import RuleRegistry

logger = logging.getLogger(__name__)


@register_dimension(
    name="plausibility",
    description="Whether data values are reasonable based on context"
)
class PlausibilityAssessor(BaseDimensionAssessor):
    """
    Assessor for the Plausibility dimension.
    
    Evaluates whether data values are reasonable based on context and whether
    this information is explicitly communicated to agents.
    """
    
    def _process_template_rules(self, connector: BaseConnector) -> Tuple[float, List[str], List[str]]:
        """
        Process template-specific rules if they are set.
        
        Args:
            connector: Data source connector
            
        Returns:
            Tuple containing:
                - score (0-20)
                - list of findings
                - list of recommendations
        """
        if not self.template_rules:
            return 0, [], []
            
        total_score = 0
        findings = []
        recommendations = []
        
        # Calculate total weight to validate it sums to 20
        total_weight = sum(rule.get('params', {}).get('weight', 0) for rule in self.template_rules)
        
        # Warn if weights don't sum to 20
        if abs(total_weight - 20) > 0.01:  # Allow for floating point precision
            logger.warning(
                f"Plausibility dimension rule weights sum to {total_weight}, not 20. "
                f"Scores may not be as expected. Consider adjusting weights to sum to 20."
            )
            findings.append(
                f"⚠️ Rule weights sum to {total_weight} instead of 20. "
                f"Each dimension should have rules totaling 20 points."
            )
        
        # Process each template rule
        for rule_config in self.template_rules:
            rule_type = rule_config.get('type')
            rule_params = rule_config.get('params', {})
            rule_weight = rule_params.get('weight', 0)
            
            # Try to get the rule class from registry
            rule_class = RuleRegistry.get_rule(f"plausibility.{rule_type.lower()}")
            if not rule_class:
                # Try without the dimension prefix
                rule_class = RuleRegistry.get_rule(rule_type.lower())
                
            if not rule_class:
                logger.warning(f"Unknown rule type: {rule_type}")
                continue
                
            # Create rule instance with template parameters
            rule = rule_class(rule_params)
            
            # Execute the rule
            try:
                result = rule.evaluate(connector)
                
                # Extract score from rule result
                rule_score = result.get('score', 0)
                
                # The rule_score represents how well the rule passed (0 to rule_weight)
                # Since weights now represent portions of 20, we use the score directly
                # but cap it at the rule's weight
                actual_score = min(rule_score, rule_weight)
                total_score += actual_score
                
                # Generate narrative for findings
                narrative = rule.generate_narrative(result)
                if narrative:
                    findings.append(f"[{rule_type}] {narrative}")
                    
                # Add score information to findings for transparency
                if actual_score < rule_weight:
                    findings.append(
                        f"[{rule_type}] Scored {actual_score:.1f}/{rule_weight} points"
                    )
                    
                # Add specific findings from rule result
                if 'column_results' in result:
                    for col, details in result.get('column_results', {}).items():
                        if details.get('outliers', 0) > 0:
                            findings.append(f"Column '{col}' has outliers: {details}")
                            
                # Add recommendations based on rule results
                if not result.get('valid', True):
                    recommendations.append(f"Address {rule_type} issues to improve data quality")
                    
            except Exception as e:
                logger.error(f"Error executing rule {rule_type}: {e}")
                findings.append(f"Failed to execute rule {rule_type}: {str(e)}")
                
        # Ensure score doesn't exceed 20
        total_score = min(total_score, 20)
        
        return total_score, findings, recommendations
    
    def assess(self, connector: BaseConnector) -> Tuple[float, List[str], List[str]]:
        """
        Assess the plausibility dimension for a data source.
        
        Args:
            connector: Data source connector
            
        Returns:
            Tuple containing:
                - score (0-20)
                - list of findings
                - list of recommendations
        """
        logger.info(f"Assessing plausibility dimension for {connector.get_name()}")
        
        findings = []
        recommendations = []
        score_components = {}
        
        # If template rules are set, use them instead of standard assessment
        if self.template_rules:
            logger.info("Using template-specific plausibility rules")
            return self._process_template_rules(connector)
        
        # Check if we're in discovery mode and have business logic enabled
        business_logic_enabled = self.config.get("business_logic_enabled", False)
        REQUIRE_EXPLICIT_METADATA = self.config.get("REQUIRE_EXPLICIT_METADATA", True)
        
        if not REQUIRE_EXPLICIT_METADATA and business_logic_enabled and hasattr(connector, 'df'):
            # Use business-focused plausibility scoring
            business_score, business_findings, business_recommendations = calculate_business_plausibility_score(
                connector.df, 
                data_type=None  # Auto-detect
            )
            
            # In discovery mode, business plausibility takes precedence
            findings.extend(business_findings)
            recommendations.extend(business_recommendations)
            
            # Start with business score as the base
            return business_score, findings, recommendations
        
        # Get plausibility information
        plausibility_info = connector.get_plausibility_results()
        
        if plausibility_info:
            # 1. Check if plausibility rules are defined
            rule_results = plausibility_info.get("rule_results", [])
            num_rules = len(rule_results)
            
            if num_rules > 0:
                findings.append(f"Plausibility rules defined: {num_rules}")
                
                # Score based on number of rules
                if num_rules >= 10:
                    score_components["rules_defined"] = 4
                elif num_rules >= 5:
                    score_components["rules_defined"] = 3
                elif num_rules >= 2:
                    score_components["rules_defined"] = 2
                else:
                    score_components["rules_defined"] = 1
                    recommendations.append("Define more plausibility rules")
                
                # 2. Check rule types
                outlier_rules = [r for r in rule_results if r.get("type") == "outlier_detection"]
                if outlier_rules:
                    findings.append(f"Outlier detection rules: {len(outlier_rules)}")
                    score_components["rule_types"] = 3
                else:
                    findings.append("No outlier detection rules defined")
                    score_components["rule_types"] = 0
                    recommendations.append("Implement outlier detection rules")
                
                # 3. Check if rules pass
                valid_overall = plausibility_info.get("valid_overall", False)
                invalid_rules = [r for r in rule_results if not r.get("valid", True)]
                
                if valid_overall:
                    findings.append("All plausibility rules pass")
                    score_components["rule_validity"] = 4
                else:
                    findings.append(f"{len(invalid_rules)} of {num_rules} plausibility rules fail")
                    if len(invalid_rules) / num_rules < 0.2:
                        score_components["rule_validity"] = 3
                    elif len(invalid_rules) / num_rules < 0.5:
                        score_components["rule_validity"] = 2
                    else:
                        score_components["rule_validity"] = 1
                    recommendations.append("Address plausibility rule violations")
                
                # 4. Check for domain-specific plausibility
                domain_rules = [
                    r for r in rule_results 
                    if "domain_specific" in r or r.get("type") == "domain_specific"
                ]
                
                if domain_rules:
                    findings.append(f"Domain-specific plausibility rules: {len(domain_rules)}")
                    score_components["domain_specific"] = 3
                else:
                    findings.append("No domain-specific plausibility rules defined")
                    score_components["domain_specific"] = 0
                    recommendations.append("Implement domain-specific plausibility checks")
                
                # 5. Evaluate whether plausibility results are communicated to agents
                if "communication_format" in plausibility_info or plausibility_info.get("explicitly_communicated"):
                    findings.append("Plausibility results are explicitly communicated to agents")
                    score_components["explicit_communication"] = 6
                else:
                    findings.append("Plausibility results are not explicitly communicated to agents")
                    score_components["explicit_communication"] = 0
                    recommendations.append("Make plausibility results explicitly available to agents")
            else:
                findings.append("No plausibility rules defined")
                recommendations.append("Define and implement basic plausibility rules")
                score_components["rules_defined"] = 0
                score_components["rule_types"] = 0
                score_components["rule_validity"] = 0
                score_components["domain_specific"] = 0
                score_components["explicit_communication"] = 0
        else:
            # No plausibility information available
            findings.append("No plausibility information is available")
            recommendations.append("Implement basic plausibility checking and expose it to agents")
            score_components["rules_defined"] = 0
            score_components["rule_types"] = 0
            score_components["rule_validity"] = 0
            score_components["domain_specific"] = 0
            score_components["explicit_communication"] = 0
        
        # Calculate overall score (0-20)
        # Weight: 
        # - rules_defined: 4 points max
        # - rule_types: 3 points max
        # - rule_validity: 4 points max
        # - domain_specific: 3 points max
        # - explicit_communication: 6 points max
        score = sum(score_components.values())
        
        # Ensure we don't exceed the maximum score
        score = min(score, 20)
        
        # Add score component breakdown to findings
        findings.append(f"Score components: {score_components}")
        
        # Add recommendations if score is not perfect
        if score < 20 and score < 10:
            recommendations.append(
                "Implement a comprehensive plausibility framework with explicit agent communication"
            )
                
        logger.info(f"Plausibility assessment complete. Score: {score}")
        return score, findings, recommendations
