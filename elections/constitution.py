import json

from unidiff import PatchSet

# Each filename corresponds to a list of pairs representing protected line
# ranges within that file, or None to protect the entire file

def _check_hunks(hunks, locks):
    for hunk in hunks:
        # diff shows 3 lines above and below for context
        # If the diff starts beyond line 0, remove the top 3 lines
        if hunk.source_start == 0:
            start = 0
        else:
            start = hunk.source_start + 3
        # If the diff starts beyond line 0 and added or removed < 6, then the
        # diff reached EOF. If not EOF, remove top 3 lines
        # This will not catch all context lines but is close enough
        if start != 0 and (hunk.added < 6 or hunk.removed < 6):
            # start + removed is the end of the patch in the source file
            end = start + hunk.removed - min(hunk.added, hunk.removed) + 3
        else:
            end = start + hunk.removed - 3

        for lock in locks:
            # If any of the diff is within or contains the protected range
            # return True
            start_prot = lock[0] < start < lock[1]
            end_prot = lock[0] < end < lock[1]
            full_prot = start < lock[0] and lock[1] < end
            return any((start_prot, end_prot, full_prot))


def is_constitutional(diff_str):
    with open('constitution.json') as f: constitution = json.load(f)
    patch = PatchSet(diff_str)
    matched_files = []

    for file in patch:
        if file in constitution:
            # File removed or renamed
            if file.is_removed_file or (file.source_file.split('/')[-1] !=
                file.target_file.split('/')[-1]):
                matched_files.append(file.path)
            locks = constitution[file.path]
            # Entire file included in constitution
            if locks is None:
                matched_files.append(file.path)
            # File overlaps with at least one protected chunk
            if _check_hunks(file, locks):
                matched_files.append(file.path)

    return matched_files


def update_constitution(diff_str):
    with open('constitution.json') as f: constitution = json.load(f)
    patch = PatchSet(diff_str)
    update = False

    for file in patch:
        if file in constitution:
            locks = constitution[file.path]
            if locks is None:
                pass
            for hunk in file:
                for lock in locks:
                    if hunk.source_start < lock[0]:
                        update = True
                        delta = hunk.added - hunk.removed
                        lock[0] += delta
                        lock[1] += delta

    if update:
        return json.dumps(constitution)
    # If no changes were necessary, return empty string to prevent file update
    return ''
