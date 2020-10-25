def find_matches(match_info, results):
    for target_match_info, obj in results:
        if target_match_info.equals(match_info):
            yield target_match_info, obj
