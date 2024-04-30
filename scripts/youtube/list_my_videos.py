#!/usr/bin/env python3

import common


def get_all_videos(youtube):
    next_page_token = ""
    all_videos = []

    while True:
        request = youtube.search().list(
            part="snippet",
            forMine=True,
            maxResults=10,
            type="video",
            pageToken=next_page_token,
        )
        response = request.execute()
        videos = response["items"]
        for video in videos:
            id = video["id"]["videoId"]
            videoUrl = f"https://www.youtube.com/watch?v={id}"
            title = video["snippet"]["title"]
            print(f"Found video: {videoUrl} {title}")
            all_videos.append(video)

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    print(f"video search done, found {len(all_videos)} videos in total")
    return all_videos


def main():
    youtube = common.get_resource()

    all_videos = get_all_videos(youtube)

    # process videos in batches, 20 videos per batch
    step = 50

    for i in range(0, len(all_videos), step):
        batch = all_videos[i : i + step]
        handle_unprocessed_videos(youtube, batch)

    for i in range(0, len(all_videos), step):
        batch = all_videos[i : i + step]
        handle_public_videos(youtube, batch)


def handle_videos(youtube, videos, statusKey, statusExpectValue):
    # get all ids
    ids = ",".join([video["id"]["videoId"] for video in videos])

    request = youtube.videos().list(
        part="snippet,contentDetails,statistics,status",
        id=ids,
    )
    response = request.execute()
    videos = response["items"]
    idx = 0
    for idx, video in videos:
        gotValue = video["status"][statusKey]
        id = video["id"]
        editUrl = "https://studio.youtube.com/video/{}/edit".format(id)
        title = video["snippet"]["title"]
        if gotValue != statusExpectValue:
            # not processed video
            idx += 1
            print(
                f"[{idx}] {statusKey} error, expect {statusExpectValue}, got {gotValue}: {editUrl} {title}"
            )


def handle_public_videos(youtube, videos):
    handle_videos(youtube, videos, "privacyStatus", "private")


def handle_unprocessed_videos(youtube, videos):
    handle_videos(youtube, videos, "uploadStatus", "processed")


if __name__ == "__main__":
    main()
