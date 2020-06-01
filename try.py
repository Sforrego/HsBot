def tracker(tracker_sheet, start_sheet, client, start=0,starting_cell=2):
    try:
        names = start_sheet.col_values(2)[1:]
    except gspread.exceptions.APIError as e:
        client.login()
        names = start_sheet.col_values(2)[1:]
    tracker_values = tracker_sheet.get_all_values()[1:]
    tracker_list = []
    if start:
        date_cell_list = tracker_sheet.range(f'AX2:AX{len(names)+1}')
    else:
        date_cell_list = tracker_sheet.range(f'AY2:AY{len(names)+1}')
    # start_list = []
    tracker_cell_list = tracker_sheet.range(f'B{starting_cell}:AW{len(names)+1}')
    # start_cell_list = start_sheet.range(f'C{starting_cell}:F{len(names)+1}')
    not_found = []

    for index,name in enumerate(names[starting_cell-2:], start=starting_cell):
        stats = getStats(playerURL(name,'iron'))
        if stats != 404:
            player_skills, player_clues , player_bosses = createDicts(parseStats(stats))
            # start_list.append((player_skills["Overall"],player_skills["Overall"],player_skills["Overall_Xp"],player_skills["Overall_Xp"]))
            player_skills = [value for key,value in player_skills.items() if "Xp" in key]

            player_skills = [x for pair in zip(player_skills,player_skills) for x in pair]

            print(f"updating {index}. {name} total {player_skills[0]} xp {player_skills[1]}")
            tracker_list.append(player_skills)
        else:

            print(f"{name} not found in highscores.")
            tracker_list.append(tracker_values[index-2][1:-2])
            not_found.append(name)

    tracker_list = [int(item) if item != "" else item for sublist in tracker_list for item in sublist]

    for i, val in enumerate(tracker_list):
        if val:
            if not start:
                if i%2==1:
                    tracker_cell_list[i].value = int(val)
            else:
                tracker_cell_list[i].value = int(val)
            if tracker_cell_list[i].value:
                tracker_cell_list[i].value = int(tracker_cell_list[i].value)


    today = datetime.now()
    today = today.strftime("%Y/%m/%d")
    for cell in date_cell_list:
        cell.value = today


    try:
        names = start_sheet.col_values(2)[1:]
    except gspread.exceptions.APIError as e:
        client.login()
        names = start_sheet.col_values(2)[1:]
    tracker_sheet.update_cells(tracker_cell_list)
    tracker_sheet.update_cells(date_cell_list)


    print("Trackers updated.")
    return not_found
