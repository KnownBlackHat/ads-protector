switch ( window.location.hostname ) {


    case "www.doubtnut.com":
        setInterval(() => {
            if (document.readyState === "complete") {
                window.location = document
                    .querySelector("#content_video_html5_api").src;
            }
        }, 1000);
        break;


    default:
        functions_to_block = [
            "akadb","checkAdblockUser","checkAdsbypasserUser"
        ];
        functions_to_block.map(func => {
            window[func] = function () {}
        } )
}
