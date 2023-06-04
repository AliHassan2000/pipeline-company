import React, { useEffect, useState } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button } from "antd";
import axios, { baseUrl } from "../../../../utils/axios";
import MultiSelect from "react-select";
import Swal from "sweetalert2";

const AddDeviceModal = (props) => {
  const getString = (str) => {
    return str ? str : "";
  };

  const getOptions = (data) => {
    return data.map((item) => {
      return { label: item, value: item };
    });
  };

  let [device, setDevice] = useState(props.editRecord);
  let [nodeName, setNodeName] = useState(
    device ? getString(device.node_name) : ""
  );
  let [pnCodes, setPnCodes] = useState(
    device ? getOptions(device.pn_codes) : []
  );
  const [pnCodeOptions, setPnCodeOptions] = useState([]);
  let [functions, setFunctions] = useState(
    device ? getOptions(device.functions) : []
  );
  const [functionOptions, setFunctionOptions] = useState([]);

  useEffect(() => {
    const serviceCalls = async () => {
      try {
        const res1 = await axios.get(baseUrl + "/getFunctions?domain=SOC");
        const res2 = await axios.post(baseUrl + "/getPnCodes?domain=SOC", {
          functions: [],
        });

        const functionOptions = getOptions(res1.data);
        setFunctionOptions(functionOptions);

        const pnCodeOptions = getOptions(res2.data);
        setPnCodeOptions(pnCodeOptions);
      } catch (err) {
        console.log(err.response);
      }
    };
    serviceCalls();
  }, []);

  const postData = async (data) => {
    try {
      await axios
        .post(baseUrl + "/addNode", data)
        .then((res) => {
          console.log(res);

          console.log(res.data);
          const promises = [];
          promises.push(
            axios
              .post(baseUrl + "/getSecurityCoverageSummaryStatus", {
                domain: "SOC",
              })
              .then((response) => {
                console.log(response.data);
                props.setData(response.data);
              })
              .catch((error) => {
                console.log(error);
              })
          );
          props.setIsModalVisible(false);
          Swal.fire(res.data.message);
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
    const functionValues = functions?.map((item) => {
      return item.value;
    });

    const pnCodeValues = pnCodes?.map((item) => {
      return item.value;
    });

    e.preventDefault();
    let data = null;
    if (device) {
      data = {
        node_id: device?.node_id,
        node_name: nodeName,
        domain: "SOC",
        functions: functionValues,
        pn_codes: pnCodeValues,
      };
    } else {
      data = {
        node_name: nodeName,
        domain: "SOC",
        functions: functionValues,
        pn_codes: pnCodeValues,
      };
    }

    postData(data);
  };

  const handleCancel = () => {
    props.setIsModalVisible(false);
  };

  const customStyles = {
    control: (provided, state) => ({
      ...provided,
      background: "#fff",
      borderColor: "#9e9e9e",
      minHeight: "30px",
      height: "30px",
      boxShadow: state.isFocused ? null : null,
    }),

    valueContainer: (provided, state) => ({
      ...provided,
      height: "30px",
      padding: "0 6px",
    }),

    input: (provided, state) => ({
      ...provided,
      margin: "0px",
    }),
    indicatorSeparator: (state) => ({
      display: "none",
    }),
    indicatorsContainer: (provided, state) => ({
      ...provided,
      height: "30px",
    }),
  };

  const handleFunctionsChange = async (e) => {
    setFunctions(e);
    let functions = e?.map((item) => item.value);
    const res = await axios.post(baseUrl + "/getPnCodes?domain=SOC", {
      functions,
    });

    const pnCodeOptions = getOptions(res.data);
    setPnCodeOptions(pnCodeOptions);

    let pnCodesFiltered = pnCodes.filter((item) =>
      res.data.includes(item.value)
    );
    setPnCodes(pnCodesFiltered);
  };

  return (
    <Modal
      style={{ marginTop: "40px", zIndex: "99999" }}
      width="50%"
      title=""
      closable={false}
      visible={props.isModalVisible}
      footer=""
    >
      <form onSubmit={handleSubmit}>
        <Row gutter={30}>
          <Col span={24} style={{ textAlign: "center" }}>
            <p style={{ fontSize: "22px" }}>{device ? "Edit" : "Add"} Node</p>
          </Col>
          <Col span={24}>
            <InputWrapper>
              Node Name: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <StyledInput
                value={nodeName}
                onChange={(e) => setNodeName(e.target.value)}
                required
              />
            </InputWrapper>
            <InputWrapper>
              Functions:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <MultiSelect
                isMulti
                styles={customStyles}
                value={functions}
                onChange={(e) => handleFunctionsChange(e)}
                options={functionOptions}
              />
            </InputWrapper>{" "}
            <InputWrapper>
              Pn Codes:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <MultiSelect
                isMulti
                styles={customStyles}
                value={pnCodes}
                onChange={(e) => setPnCodes(e)}
                options={pnCodeOptions}
              />
            </InputWrapper>
          </Col>
          <Col span={24} style={{ textAlign: "center", paddingTop: "20px" }}>
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
