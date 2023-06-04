import React from "react";
import { Modal } from "antd";
import SeedInfo from "./SeedInfo";

const ShowSeedDevice = (porps) => {
  const { showSeed,setShowSeed ,seedRecord} = porps;
  const handleOk = () => {
    setShowSeed(false);
  };

  return (
    <>
      <Modal
        title="Seed Device Detail"
        width="65%"
        visible={porps.showSeed}
        closable={false}
        onOk={handleOk}
        cancelButtonProps={{ style: { display: "none" } }}
      >
        <div className="modal_header"> 
        </div>
        <SeedInfo seedRecord={seedRecord} />
      </Modal>
    </>
  );
};

export default ShowSeedDevice;
