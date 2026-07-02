def calculate_priority_score(instance):
    """
    Calculates the priority score for a RequirementRequest instance.
    Returns None if Workload is 'pending'.
    """
    if instance.workload == 'pending':
        return None

    score = 0

    # Requirement Type Weights
    type_scores = {
        'regulatory': 50,
        'security': 40,
        'bug': 30,
        'revenue': 20,
        'cost': 10,
        'optimization': 0,
    }
    score += type_scores.get(instance.requirement_type, 0)

    # Impacted Users Weights
    user_scores = {
        '>1000': 40,
        '500-1000': 30,
        '100-500': 20,
        '<100': 10,
    }
    score += user_scores.get(instance.impacted_users, 0)

    # Revenue Impact Weights
    revenue_scores = {
        '>1M': 50,
        '300k-1M': 30,
        '50k-300k': 20,
        '<50k': 10,
    }
    score += revenue_scores.get(instance.revenue_impact, 0)

    # Supplementary Materials Weights (+5 per item, max +20)
    if instance.supplementary_materials:
        score += min(len(instance.supplementary_materials) * 20, 50)

    # Workload Weights (Quick wins prioritized)
    workload_scores = {
        'small': 50,
        'medium': 10,
        'large': -10,
    }
    score += workload_scores.get(instance.workload, 0)

    return score
