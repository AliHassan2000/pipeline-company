import React, { useState, useEffect } from "react";
import styled from "styled-components";
import {
  Row,
  Col,
  Modal,
  Input,
  Button,
  Select,
  DatePicker,
  Space,
} from "antd";
import axios, { baseUrl } from "../../../../utils/axios";
import Swal from "sweetalert2";
import moment from "moment";
import Attachment from "./attachment";

const AddDeviceModal = (props) => {
  const { Option } = Select;

  let [deviceIds, setDeviceIds] = useState([]);
  let [deviceIdOptions, setDeviceIdOptions] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const res1 = await axios.get(baseUrl + "/getDismantleDeviceId");
        setDeviceIds(res1.data);
      } catch (err) {
        console.log(err.response);
      }
    })();
  }, []);
  useEffect(() => {
    getDeviceOptions(deviceIds);
  }, [deviceIds]);

  const getDeviceOptions = (values = []) => {
    let options = [];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    setDeviceIdOptions(options);
  };

  const getString = (str) => {
    return str ? str : "";
  };

  const regex = "^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|[1][012])-[0-9]{4}$";

  let [device, setDevice] = useState(props.editRecord);
  let [ip, setIp] = useState(
    device ? getString(device.ipt_rma_tracker_id) : ""
  );
  let [rmaOrderNumber, setRMAOrderNumber] = useState(
    device ? getString(device.rma_order_number) : ""
  );
  let [serviceRequestNumber, setServiceRequestNumber] = useState(
    device ? getString(device.service_request_number) : ""
  );
  let [sn, setSN] = useState(device ? getString(device.serial_number) : "");
  let [mac, setMac] = useState(device ? getString(device.mac) : "");
  //   let [userId, setUserId] = useState(device ? getString(device.user_id) : "");
  let [userInfoAndDeviceImpactedDetails, setUserInfoAndDeviceImpactedDetails] =
    useState(
      device ? getString(device.user_info_and_device_impacted_details) : ""
    );
  let [rmaOrderedDate, setRMAOrderedDate] = useState(
    device ? getString(device.rma_ordered_date) : null
  );
  let [FEReceivingTheRMAPartFromDHL, setFEReceivingTheRMAPartFromDHL] =
    useState(
      device ? getString(device.fe_receiving_the_rma_part_from_dhl) : ""
    );
  let [currentStatus, setCurrentStatus] = useState(
    device ? getString(device.current_status) : ""
  );
  let [actualRMAReceivedDate, setActualRMAReceivedDate] = useState(
    device ? getString(device.actual_rma_received_date) : null
  );
  //   let [partNumber, setPartNumber] = useState(
  //     device ? getString(device.part_number) : ""
  //   );
  let [engineerHandlingTheRMA, setEngineerHandlingTheRMA] = useState(
    device ? getString(device.engineer_handling_the_rma) : null
  );
  let [pickupDateScheduledInAirwayBill, setPickupDateScheduledInAirwayBill] =
    useState(
      device ? getString(device.pickup_date_scheduled_in_airway_bill) : null
    );
  let [feDeliveringTheDeviceToDHL, setFEDeliveringTheDeviceToDHL] = useState(
    device ? getString(device.fe_delivering_the_device_to_dhl) : ""
  );
  let [deliveryLocation, setDeliveryLocation] = useState(
    device ? getString(device.delivery_location) : ""
  );
  let [finalStatus, setFinalStatus] = useState(
    device ? getString(device.final_status) : ""
  );
  let [remarks, setRemarks] = useState(device ? getString(device.remarks) : "");

  // let [macs, setMacs] = useState([]);
  // let [macOptions, setMacOptions] = useState([]);
  let [engineerHandlingTheRMAs, setEngineerHandlingTheRMAs] = useState([]);
  let [engineerHandlingTheRMAOptions, setEngineerHandlingTheRMAOptions] =
    useState([]);
  let [attachments, setAttachments] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        // const res = await axios.get(baseUrl + "/getMacs");
        // setMacs(res.data);
        // if (mac === "") {
        //   setMac(res?.data[0]);
        // }

        const res1 = await axios.get(baseUrl + "/getAssigneesTracker");
        setEngineerHandlingTheRMAs(res1.data);
        if (engineerHandlingTheRMA === "") {
          setEngineerHandlingTheRMA(res1?.data[0]);
        }
      } catch (err) {
        console.log(err.response);
      }
    })();
  }, []);

  // useEffect(() => {
  //   let options = getOptions(macs);
  //   setMacOptions(options);
  // }, [macs]);

  useEffect(() => {
    let options = getOptions(engineerHandlingTheRMAs);
    setEngineerHandlingTheRMAOptions(options);
  }, [engineerHandlingTheRMAs]);

  const getOptions = (values = []) => {
    let options = [];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    return options;
  };

  const openSweetAlert = (title, type) => {
    Swal.fire({
      title,
      type,
    });
  };

  const postDevice = async (device) => {
    try {
      await axios
        .post(baseUrl + "/iptRMATracker?category=ipt_rma_tracker", device)
        .then((response) => {
          if (response?.response?.status == 500) {
            openSweetAlert(response?.response?.data?.response, "error");
          } else {
            openSweetAlert("Item Added/Updated Successfully", "success");
          }
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/iptRMATracker")
              .then((response) => {
                console.log(response.data);
                props.setDataSource(response.data);
                props.excelData = response.data;
              })
              .catch((error) => {
                console.log(error);
              })
          );
          return Promise.all(promises);
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
    if (
      rmaOrderedDate ||
      actualRMAReceivedDate ||
      pickupDateScheduledInAirwayBill
    ) {
      const device = [
        {
          ipt_rma_tracker_id: ip,
          rma_order_number: rmaOrderNumber,
          service_request_number: serviceRequestNumber,
          //   sn,
          serial_number: sn,
          mac,
          //   user_id: userId,
          user_info_and_device_impacted_details:
            userInfoAndDeviceImpactedDetails,
          rma_ordered_date: rmaOrderedDate,
          fe_receiving_the_rma_part_from_dhl: FEReceivingTheRMAPartFromDHL,
          current_status: currentStatus,
          actual_rma_received_date: actualRMAReceivedDate,
          //   part_number: partNumber,
          engineer_handling_the_rma: engineerHandlingTheRMA,
          pickup_date_scheduled_in_airway_bill: pickupDateScheduledInAirwayBill,
          fe_delivering_the_device_to_dhl: feDeliveringTheDeviceToDHL,
          delivery_location: deliveryLocation,
          final_status: finalStatus,
          attachments,
          remarks,
        },
      ];

      props.setIsModalVisible(false);
      postDevice(device);
    } else {
      alert("Dates can not be empty :)");
    }
  };

  const handleCancel = async () => {
    props.setIsModalVisible(false);
    if (attachments.length > 0) {
      await axios
        .post(baseUrl + "/deleteAttachmentsByName", { attachments })
        .then((response) => {})
        .catch((err) => {
          console.log(err);
        });
    }
  };

  return (
    <Modal
      style={{ marginTop: "-60px", zIndex: "99999" }}
      width="80%"
      title=""
      closable={false}
      visible={props.isModalVisible}
      footer=""
    >
      <form onSubmit={handleSubmit}>
        <Row gutter={30}>
          <Col span={24} style={{ textAlign: "center" }}>
            <p style={{ fontSize: "22px" }}>
              {device ? "Edit" : "Add"} IPT RMA Tracker
            </p>
          </Col>
          <Col span={12}>
            <InputWrapper>
              {device ? (
                <>
                  Mac:
                  {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
                  &nbsp;&nbsp;
                  <StyledInput
                    value={mac}
                    onChange={(e) => setMac(e.target.value)}
                    // required
                  />
                  {/* <Select style={{ width: "100%" }} value={mac} disabled /> */}
                </>
              ) : (
                <>
                  Mac:
                  {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
                  &nbsp;&nbsp;
                  <StyledInput
                    value={mac}
                    onChange={(e) => setMac(e.target.value)}
                    // required
                  />
                  {/* <Select
                    value={mac}
                    style={{ width: "100%" }}
                    onChange={(value) => {
                      setMac(value);
                    }}
                    showSearch
                    optionFilterProp="children"
                    filterOption={(input, option) =>
                      option.children
                        .toLowerCase()
                        .indexOf(input.toLowerCase()) >= 0
                    }
                  >
                    {macOptions}
                  </Select> */}
                </>
              )}
            </InputWrapper>
            <InputWrapper>
              RMA Order Number: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={rmaOrderNumber}
                onChange={(e) => setRMAOrderNumber(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Service Request Number: &nbsp;
              <span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={serviceRequestNumber}
                onChange={(e) => setServiceRequestNumber(e.target.value)}
                required
              />
            </InputWrapper>
            {/* <InputWrapper>
              Serial Number: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={sn}
                onChange={(e) => setSN(e.target.value)}
                required
              />
            </InputWrapper> */}
            {/* <InputWrapper>
              User Id: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                required
              />
            </InputWrapper> */}
            <InputWrapper>
              User Info and Device Impacted Details: &nbsp;
              <span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={userInfoAndDeviceImpactedDetails}
                onChange={(e) =>
                  setUserInfoAndDeviceImpactedDetails(e.target.value)
                }
                required
              />
            </InputWrapper>
            <InputWrapper>
              RMA Ordered Date: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <DatePicker
                onChange={(date, dateString) => {
                  setRMAOrderedDate(dateString);
                }}
                defaultValue={
                  rmaOrderedDate ? moment(rmaOrderedDate, "DD-MM-YYYY") : null
                }
                style={{ width: "100%" }}
                format="DD-MM-YYYY"
                required
              />
            </InputWrapper>
            <InputWrapper>
              FE Receiving the RMA part from DHL: &nbsp;
              <span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={FEReceivingTheRMAPartFromDHL}
                onChange={(e) =>
                  setFEReceivingTheRMAPartFromDHL(e.target.value)
                }
                required
              />
            </InputWrapper>
            <InputWrapper>
              Current Status: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={currentStatus}
                onChange={(e) => setCurrentStatus(e.target.value)}
                required
              />
            </InputWrapper>

            {/* <InputWrapper>
              Handback Status: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={handbackStatus}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setHandbackStatus(value);
                }}
                required
              >
                <Option value="Completed">Completed</Option>
                <Option value="Pending">Pending</Option>
              </Select>
            </InputWrapper> */}
          </Col>

          <Col span={12}>
            <InputWrapper>
              Actual RMA Received Date: &nbsp;
              <span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <DatePicker
                onChange={(date, dateString) => {
                  setActualRMAReceivedDate(dateString);
                }}
                defaultValue={
                  actualRMAReceivedDate
                    ? moment(actualRMAReceivedDate, "DD-MM-YYYY")
                    : null
                }
                style={{ width: "100%" }}
                format="DD-MM-YYYY"
                required
              />
            </InputWrapper>
            {/* <InputWrapper>
              Part Number: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={partNumber}
                onChange={(e) => setPartNumber(e.target.value)}
                required
              />
            </InputWrapper> */}
            <InputWrapper>
              Engineer Handling the RMA: &nbsp;
              <span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={engineerHandlingTheRMA}
                style={{ width: "100%" }}
                onChange={(value) => {
                  setEngineerHandlingTheRMA(value);
                }}
                showSearch
                optionFilterProp="children"
                filterOption={(input, option) =>
                  option.children.toLowerCase().indexOf(input.toLowerCase()) >=
                  0
                }
              >
                {engineerHandlingTheRMAOptions}
              </Select>
            </InputWrapper>
            <InputWrapper>
              Pickup Date Scheduled in Airway Bill: &nbsp;
              <span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <DatePicker
                onChange={(date, dateString) => {
                  setPickupDateScheduledInAirwayBill(dateString);
                }}
                defaultValue={
                  pickupDateScheduledInAirwayBill
                    ? moment(pickupDateScheduledInAirwayBill, "DD-MM-YYYY")
                    : null
                }
                style={{ width: "100%" }}
                format="DD-MM-YYYY"
                required
              />
            </InputWrapper>
            <InputWrapper>
              FE Delivering the Device to DHL:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={feDeliveringTheDeviceToDHL}
                onChange={(e) => setFEDeliveringTheDeviceToDHL(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Delivery Location: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={deliveryLocation}
                onChange={(e) => setDeliveryLocation(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Final Status:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={finalStatus}
                onChange={(e) => setFinalStatus(e.target.value)}
                // required
              />
            </InputWrapper>
            <InputWrapper>
              Remarks:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
                // required
              />
            </InputWrapper>
          </Col>
          <Col span={24}>
            {/* <InputWrapper> */}
            Attachments:
            {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
            &nbsp;&nbsp;
            <Attachment response={attachments} setResponse={setAttachments} />
            {/* </InputWrapper> */}
          </Col>

          <Col span={24} style={{ textAlign: "center", marginTop: "60px" }}>
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

export default AddDeviceModal;

const StyledInput = styled(Input)`
  height: 1.8rem;
`;

const InputWrapper = styled.div`
  white-space: nowrap;
  display: flex;
  justify-content: space-between;
  padding-bottom: 10px;
`;

const StyledSubmitButton = styled(Input)`
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
