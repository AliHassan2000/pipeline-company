import React, { useState } from "react";
import { Button, Upload } from "antd";
import axios, { baseUrl } from "../../../../utils/axios";
// import Dragger from "antd/es/upload/Dragger";

const Attachment = ({ response, setResponse }) => {
  const [fileList, setFileList] = useState([]);

  const api = `/attachmentFile`;

  const props = {
    name: "attachment",
    multiple: false,
    listType: "picture",
    maxCount: 2,
    action: baseUrl + api,
    onChange(info) {
      const { status } = info.file;
      let newFileList = [...info.fileList];
      setFileList(newFileList);
      if (status === "uploading") {
        console.log("uploading", info);
      }
      if (status === "done") {
        let temp = response;
        temp?.push(info.file.response);
        setResponse(temp);
        console.log("done", info);
      }
      if (status === "error") {
        console.log(info);
      }
    },
    onRemove(e) {
      console.log(e);
      axios
        .post(baseUrl + "/deleteAttachmentsByName", {
          attachments: [e.response],
        })
        .then((response) => {})
        .catch((err) => {
          console.log(err);
        });
    },
  };

  return (
    <Upload {...props} fileList={fileList}>
      <Button>Click here to upload files</Button>
    </Upload>
  );
};

export default Attachment;
