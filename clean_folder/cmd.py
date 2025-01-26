if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="App for sorting files in specific folder"
    )
    parser.add_argument("-f", "--folder", default=True)

    args = vars(parser.parse_args())
    folder_path = args.get("folder")
    current_folder = Path(folder_path)

    points = "-" * 100
    FOLDERS = [current_folder.joinpath(new_dir) for new_dir in new_directory]

    main()
