import React, { useState, useEffect } from "react";
import { Modal, Button } from "antd";
import DeviceInfo from "./DeviceInfo";
// import { StyledSubMenu } from "../landing/styles/main.styles";

const ShowDeviceModal = (porps) => {
  const { deviceData } = porps;

  const handleOk = () => {
    porps.setIsModalVisible(false);
  };

  return (
    <>
      <Modal
        title="Device Detail"
        width="70%"
        visible={porps.isModalVisible}
        closable={false}
        onOk={handleOk}
        cancelButtonProps={{ style: { display: "none" } }}
      >
        <div className="modal_header">
          <p
            style={{
              paddingLeft: "9%",
              fontSize: "18px",
              // fontWeight: "bolder",
            }}
          >
            Device Source
          </p>
          <p
            style={{
              // paddingLeft: "55%",
              fontSize: "18px",
              // fontWeight: "bolder",
            }}
          >
            Device Information
          </p>
        </div>
        <DeviceInfo data={deviceData} />
      </Modal>
    </>
  );
};

export default ShowDeviceModal;
