import React, { useState, useEffect } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button, Select } from "antd";
import axios, { baseUrl } from "../../../../utils/axios";
import Swal from "sweetalert2";

const AddDeviceModal = (props) => {
  const { Option } = Select;

  const getString = (str) => {
    return str ? str : "";
  };

  const regex = "^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|[1][012])-[0-9]{4}$";
  let [device, setDevice] = useState(props.editRecord);
  /////////////////////////////
  let [ip, setIp] = useState(device ? getString(device.rack_id) : "");
  let [siteId, setSiteId] = useState(device ? getString(device.site_id) : "");
  let [rackName, setRackName] = useState(
    device ? getString(device.rack_name) : ""
  );
  let [manufactureDate, setManufactureDate] = useState(
    device ? getString(device.manufactuer_date) : ""
  );
  let [unitPosition, setUnitPosition] = useState(
    device ? getString(device.unit_position) : ""
  );
  let [rackModel, setRackModel] = useState(
    device ? getString(device.rack_model) : ""
  );
  let [pnCode, setPnCode] = useState(device ? getString(device.pn_code) : "");
  let [serialNumber, setSerialNumber] = useState(
    device ? getString(device.serial_number) : ""
  );
  let [ru, setRu] = useState(device ? getString(device.ru) : "42");
  let [height, setHeight] = useState(
    device ? getString(device.height) : "78.39"
  );
  let [width, setWidth] = useState(device ? getString(device.width) : "23.62");
  let [depth, setDepth] = useState(device ? getString(device.depth) : "42.13");
  let [floor, setFloor] = useState(device ? getString(device.floor) : "");
  let [status, setStatus] = useState(
    device ? getString(device.status) : "Production"
  );
  let [tagId, setTagId] = useState(device ? getString(device.tag_id) : "");
  let [rfsDate, setRfsDate] = useState(
    device ? getString(device.rfs_date) : ""
  );
  // let [itemCode, setItemCode] = useState(
  //   device ? getString(device.item_code) : ""
  // );
  // let [itemDesc, setItemDesc] = useState(
  //   device ? getString(device.item_desc) : ""
  // );
  // let [clei, setClei] = useState(device ? getString(device.clei) : "");

  let [siteIds, setSiteIds] = useState([]);
  let [siteIdOptions, setSiteIdOptions] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const res1 = await axios.get(baseUrl + "/getAllSiteIDs");
        setSiteIds(res1.data);
      } catch (err) {
        console.log(err.response);
      }
    })();
  }, []);

  useEffect(() => {
    getSiteIdOptions(siteIds);
  }, [siteIds]);

  const getSiteIdOptions = (values = []) => {
    let options = [];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    setSiteIdOptions(options);
    // return options;
  };

  const openSweetAlert = (title, type) => {
    Swal.fire({
      title,
      type,
    });
  };

  const postDevice = async (device) => {
    try {
      //console.log(device);
      await axios
        .post(baseUrl + "/addRacks", device)
        .then((response) => {
          if (response?.response?.status == 500) {
            openSweetAlert(response?.response?.data?.response, "error");
          } else {
            openSweetAlert(
              `Rack ${device ? "Updated" : "Added"} Successfully`,
              "success"
            );
            const promises = [];
            promises.push(
              axios
                .get(baseUrl + "/getAllRacks")
                .then((response) => {
                  console.log(response.data);
                  props.setDataSource(response.data);
                  props.setRowCount(response.data.length);
                  props.excelData = response.data;
                })
                .catch((error) => {
                  console.log(error);
                })
            );
            return Promise.all(promises);
          }
        })
        .catch((err) => {
          console.log(err);
        });
    } catch (err) {
      console.log(err);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const device = {
      rack_id: ip,
      site_id: siteId,
      rack_name: rackName,
      manufactuer_date: manufactureDate,
      unit_position: unitPosition,
      rack_model: rackModel,
      pn_code: pnCode,
      serial_number: serialNumber,
      ru,
      height,
      width,
      depth,
      floor,
      status,
      tag_id: tagId,
      rfs_date: rfsDate,
    };

    props.setIsModalVisible(false);
    postDevice(device);
  };

  const handleCancel = () => {
    props.setIsModalVisible(false);
  };

  const getOptions = (values = []) => {
    let options = [];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    return options;
  };

  return (
    <Modal
      style={{ marginTop: "0px", zIndex: "99999" }}
      width="50%"
      title=""
      closable={false}
      visible={props.isModalVisible}
      footer=""
    >
      <form onSubmit={handleSubmit}>
        <Row gutter={30}>
          <Col span={24} style={{ textAlign: "center" }}>
            <p style={{ fontSize: "22px" }}>{device ? "Edit" : "Add"} Rack</p>
          </Col>
          <Col span={12}>
            {/* <InputWrapper>
              Rack Id: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              {device ? (
                <StyledInput value={ip} readonly />
              ) : (
                <StyledInput
                  value={ip}
                  onChange={(e) => setIp(e.target.value)}
                  required
                />
              )}
            </InputWrapper> */}
            <InputWrapper>
              Rack Name: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              {/* {device ? (
                <StyledInput value={rackName} disabled />
              ) : ( */}
              <StyledInput
                value={rackName}
                onChange={(e) => setRackName(e.target.value)}
                required
              />
              {/* )} */}
            </InputWrapper>
            <InputWrapper>
              Site Id: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={siteId}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setSiteId(value);
                }}
                showSearch
                // placeholder="Select a person"
                optionFilterProp="children"
                // onSearch={onSearch}
                filterOption={(input, option) =>
                  option.children.toLowerCase().indexOf(input.toLowerCase()) >=
                  0
                }
              >
                {siteIdOptions}
              </Select>
              {/* <StyledInput
                value={siteId}
                onChange={(e) => setSiteId(e.target.value)}
                required
              /> */}
            </InputWrapper>

            <InputWrapper>
              Manufacture Date: &nbsp;&nbsp;
              <StyledInput
                value={manufactureDate}
                onChange={(e) => setManufactureDate(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Unit Position: &nbsp;&nbsp;
              <StyledInput
                value={unitPosition}
                onChange={(e) => setUnitPosition(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Rack Model: &nbsp;&nbsp;
              <StyledInput
                value={rackModel}
                onChange={(e) => setRackModel(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Pn Code: &nbsp;&nbsp;
              <StyledInput
                value={pnCode}
                onChange={(e) => setPnCode(e.target.value)}
                // required
              />
            </InputWrapper>

            <InputWrapper>
              Serial Number: &nbsp;&nbsp;
              <StyledInput
                value={serialNumber}
                onChange={(e) => setSerialNumber(e.target.value)}
                // required
              />
            </InputWrapper>
          </Col>
          <Col span={12}>
            <InputWrapper>
              Ru: &nbsp;&nbsp;
              <StyledInput
                value={ru}
                onChange={(e) => setRu(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Height: &nbsp;&nbsp;
              <StyledInput
                value={height}
                onChange={(e) => setHeight(e.target.value)}
                // required
              />
            </InputWrapper>

            <InputWrapper>
              Width: &nbsp;&nbsp;
              <StyledInput
                value={width}
                onChange={(e) => setWidth(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Depth: &nbsp;&nbsp;
              <StyledInput
                value={depth}
                onChange={(e) => setDepth(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Floor: &nbsp;&nbsp;
              <StyledInput
                value={floor}
                onChange={(e) => setFloor(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Status: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={status}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setStatus(value);
                }}
                required
              >
                {getOptions(["Production", "Dismantle", "Duplicate"])}
              </Select>
              {/* <StyledInput
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                required
              /> */}
            </InputWrapper>
            <InputWrapper>
              Tag Id: &nbsp;&nbsp;
              <StyledInput
                value={tagId}
                onChange={(e) => setTagId(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              RFS Date: &nbsp;&nbsp;
              <StyledInput
                pattern={regex}
                placeholder="dd-mm-yyyy"
                value={rfsDate}
                onChange={(e) => setRfsDate(e.target.value)}
                // required
              />
            </InputWrapper>
            {/* <InputWrapper>
              Item Code:&nbsp;&nbsp;
              <StyledInput
                value={itemCode}
                onChange={(e) => setItemCode(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Item Desc: &nbsp;&nbsp;
              <StyledInput
                value={itemDesc}
                onChange={(e) => setItemDesc(e.target.value)}
                required
              />
            </InputWrapper>
             */}
            {/* <InputWrapper>
              Clei:&nbsp;&nbsp;
              <StyledInput
                value={clei}
                onChange={(e) => setClei(e.target.value)}
                // required
              />
            </InputWrapper> */}
          </Col>
          <Col span={24} style={{ textAlign: "center" }}>
            <StyledButton color={"red"} onClick={handleCancel}>
              Cancel
            </StyledButton>
            &nbsp; &nbsp;{" "}
            <StyledSubmitButton color={"green"} type="submit" value="Done" />
          </Col>
        </Row>
      </form>
    </Modal>
  );
};

const StyledInput = styled(Input)`
  height: 1.6rem;
`;

const InputWrapper = styled.div`
  font-size: 12px;
  white-space: nowrap;
  display: flex;
  justify-content: space-between;
  padding-bottom: 10px;
`;

const StyledSubmitButton = styled(Input)`
  font-size: 11px;
  font-weight: bolder;
  width: 15%;
  font-family: Montserrat-Regular;
  box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
  background-color: ${(props) => props.color};
  border-color: ${(props) => props.color};
  color: white;
  border-radius: 5px;
  &:focus,
  &:hover {
    background-color: ${(props) => props.color};
    border-color: ${(props) => props.color};
    color: white;
    opacity: 0.8;
  }
`;

const StyledButton = styled(Button)`
  height: 27px;
  font-size: 11px;
  font-weight: bolder;
  width: 15%;
  font-family: Montserrat-Regular;
  box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
  background-color: ${(props) => props.color};
  border-color: ${(props) => props.color};
  color: white;
  border-radius: 5px;
  &:focus,
  &:hover {
    background-color: ${(props) => props.color};
    border-color: ${(props) => props.color};
    color: white;
    opacity: 0.8;
  }
`;

export default AddDeviceModal;
