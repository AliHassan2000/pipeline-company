import React, { useState, useRef, useEffect } from "react";
import styled from "styled-components";
import {
  Table,
  Button,
  Menu,
  Dropdown,
  Space,
  notification,
  Spin,
  Input,
  Select,
  Row,
  Col,
} from "antd";
import XLSX from "xlsx";
import axios, { baseUrl } from "../../../utils/axios";
import Search from "../../../components/search";
import { StyledTable } from "../../../components/table/main.styles";
import { StyledHeading } from "../../../components/paragraph/main.styles";
import {
  PlusOutlined,
  RightSquareOutlined,
  ReloadOutlined,
  EditOutlined,
  DownOutlined,
} from "@ant-design/icons";
import Swal from "sweetalert2";
import { columnSearch } from "../../../utils";
import useWindowDimensions from "../../../hooks/useWindowDimensions";
import { roles } from "../../../utils/constants.js";
import Modal from "./modal";

let filters = null;
const Index = (props) => {
  const { height, width } = useWindowDimensions();
  const { Option } = Select;
  const [user, setUser] = useState();
  let [loading, setLoading] = useState(false);
  let [sortedInfo, setSortedInfo] = useState(null);
  let [filteredInfo, setFilteredInfo] = useState(null);
  let [total, setTotal] = useState(0);
  let [dataSource, setDataSource] = useState([]);
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  const [rowCount, setRowCount] = useState(0);
  let getColumnSearchProps = columnSearch(
    searchText,
    setSearchText,
    searchedColumn,
    setSearchedColumn
  );
  const [pageSize, setPageSize] = useState(50);
  const [currentPage, setCurrentPage] = useState(1);
  const [updateDisabled, setUpdateDisabled] = useState(true);

  let [domain, setDomain] = useState("");
  let [pnCode, setPnCode] = useState("");
  let [functiond, setFunction] = useState("");
  let [deviceId, setDeviceId] = useState("");

  let [domains, setDomains] = useState([]);
  let [pnCodes, setPnCodes] = useState([]);
  let [functions, setFunctions] = useState([]);
  let [deviceIds, setDeviceIds] = useState([]);

  const [paamIntegrations, setPAAMIntegrations] = useState("");
  const [aaaIntegrations, setAAAIntegrations] = useState("");
  const [mbssApproved, setMBSSApproved] = useState("");
  const [mbssCompliance, setMBSSCompliance] = useState("");

  useEffect(() => {
    const serviceCalls = async () => {
      setLoading(true);
      const res = await axios.get(baseUrl + "/getDomains");
      setDomains(res.data);

      if (res?.data?.length > 0) {
        setDomain(res?.data[0]);

        const res1 = await axios.get(
          baseUrl + `/getFunctionsForBulkUpdate?domain=${res?.data[0]}`
        );
        setFunctions(res1.data);

        const res2 = await axios.post(baseUrl + `/getPnCodesForBulkUpdate`, {
          domain: res?.data[0],
          function: "",
        });
        setPnCodes(res2.data);

        const res3 = await axios.post(baseUrl + `/getDeviceIdsForBulkUpdate`, {
          domain: res?.data[0],
          function: "",
          pn_code: "",
        });
        setDeviceIds(res3.data);
      }

      setLoading(false);
    };
    serviceCalls();
  }, []);

  const getOptions = (values = []) => {
    let options = [<Option value="">Choose filter value</Option>];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    return options;
  };

  const getDomainOptions = (values = []) => {
    let options = [];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    return options;
  };

  const getDataBySearchFilters = async (filters) => {
    // let response = {
    //   data: {
    //     data: [{ device_id: "1" }, { device_id: "2" }, { device_id: "3" }],
    //     device_ids: ["1", "2", "3"],
    //   },
    // };
    // setRowCount(response.data.data.length);
    // setDataSource(response.data.data);
    // setSelectedRowKeys(response.data.device_ids);

    setLoading(true);
    await axios
      .post(baseUrl + "/getDevicesBySearchFiltersNonPaginated", filters)
      .then((response) => {
        setRowCount(response.data.data.length);
        setDataSource(response.data.data);
        setSelectedRowKeys(response.data.device_ids);
        // setTotal(response.data.total);
        setLoading(false);
      })
      .catch((error) => {
        console.log(error);
        setLoading(false);
      });
  };

  const getDataBySearchFiltersAfterUpdate = async (filters) => {
    setLoading(true);
    await axios
      .post(baseUrl + "/getDevicesBySearchFiltersNonPaginated", filters)
      .then((response) => {
        setRowCount(response.data.data.length);
        setDataSource(response.data.data);
        // setTotal(response.data.total);
        setLoading(false);
      })
      .catch((error) => {
        console.log(error);
        setLoading(false);
      });
  };

  const handleSubmit = () => {
    setUpdateDisabled(false);
    filters = {
      domain,
      pn_code: pnCode,
      function: functiond,
      device_id: deviceId,
    };

    getDataBySearchFilters(filters);
  };

  const update = async (data) => {
    try {
      // setLoading(true);
      await axios
        .post(baseUrl + "/bulkUpdateDeviceColumns", data)
        .then((res) => {
          // setLoading(false);
          console.log(res);
          // alert("successfully updated");
          getDataBySearchFiltersAfterUpdate(filters);
          Swal.fire("successfully updated");
        })
        .catch((err) => {
          // setLoading(false);
          // alert(err);
          console.log(err);
        });
    } catch (err) {
      // setLoading(false);
      // alert(err);
      console.log(err);
    }
  };

  const handleUpdate = () => {
    const data = {
      device_ids: selectedRowKeys,
      values: {
        paam_integrations: paamIntegrations,
        aaa_integrations: aaaIntegrations,
        mbss_approved: mbssApproved,
        mbss_compliance: mbssCompliance,
      },
    };

    update(data);
  };

  const handleCancel = async () => {
    setUpdateDisabled(true);
    setPnCode("");
    setFunction("");
    setDeviceId("");
    setDataSource([]);
    setPAAMIntegrations("");
    setAAAIntegrations("");
  };

  const onSelectChange = (selectedRowKeys) => {
    console.log("selectedRowKeys changed: ", selectedRowKeys);
    setSelectedRowKeys(selectedRowKeys);
  };

  const rowSelection = {
    selectedRowKeys,
    onChange: onSelectChange,
    selection: Table.SELECTION_ALL,
    hideSelectAll: true,
  };

  const handleChange = (pagination, filters, sorter, extra) => {
    console.log("Various parameters", pagination, filters, sorter, extra);
    // handleSubmit();
    // setPageSize(pagination.pageSize);
    // setCurrentPage(pagination.current);
    setRowCount(extra.currentDataSource.length);
    setFilteredInfo(filters);
    setSortedInfo(sorter);
  };

  sortedInfo = sortedInfo || {};
  filteredInfo = filteredInfo || {};

  const columns = [
    {
      title: "Ip Address",
      dataIndex: "ne_ip_address",
      key: "ne_ip_address",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Device Id",
      dataIndex: "device_id",
      key: "device_id",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Device Name",
      dataIndex: "device_name",
      key: "device_name",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Rack Id",
      dataIndex: "rack_id",
      key: "rack_id",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Site Id",
      dataIndex: "site_id",
      key: "site_id",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Manufacture Date",
      dataIndex: "manufactuer_date",
      key: "manufactuer_date",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Virtual",
      dataIndex: "virtual",
      key: "virtual",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Authentication",
      dataIndex: "authentication",
      key: "authentication",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Item Code",
      dataIndex: "item_code",
      key: "item_code",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Item Desc",
      dataIndex: "item_desc",
      key: "item_desc",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Clei",
      dataIndex: "clei",
      key: "clei",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Subrack Id Number",
      dataIndex: "subrack_id_number",
      key: "subrack_id_number",
      align: "center",
      ellipsis: true,
    },
    {
      title: "HW EOS Date",
      dataIndex: "hw_eos_date",
      key: "hw_eos_date",
      align: "center",
      ellipsis: true,
    },
    {
      title: "HW EOL Date",
      dataIndex: "hw_eol_date",
      key: "hw_eol_date",
      align: "center",
      ellipsis: true,
    },
    {
      title: "SW EOS Date",
      dataIndex: "sw_eos_date",
      key: "sw_eos_date",
      align: "center",
      ellipsis: true,
    },
    {
      title: "SW EOL Date",
      dataIndex: "sw_eol_date",
      key: "sw_eol_date",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Criticality",
      dataIndex: "criticality",
      key: "criticality",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Function",
      dataIndex: "function",
      key: "function",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Domain",
      dataIndex: "domain",
      key: "domain",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Cisco Domain",
      dataIndex: "cisco_domain",
      key: "cisco_domain",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Patch Version",
      dataIndex: "patch_version",
      key: "patch_version",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Section",
      dataIndex: "section",
      key: "section",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Software Version",
      dataIndex: "software_version",
      key: "software_version",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Hardware Version",
      dataIndex: "hardware_version",
      key: "hardware_version",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Department",
      dataIndex: "department",
      key: "department",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Serial Number",
      dataIndex: "serial_number",
      key: "serial_number",
      align: "center",
      ellipsis: true,
    },
    {
      title: "RFS",
      dataIndex: "rfs_date",
      key: "rfs_date",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Dismantle Date",
      dataIndex: "dismantle_date",
      key: "dismantle_date",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Pn Code",
      dataIndex: "pn_code",
      key: "pn_code",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Tag Id",
      dataIndex: "tag_id",
      key: "tag_id",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Max Power",
      dataIndex: "max_power",
      key: "max_power",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Device Ru",
      dataIndex: "device_ru",
      key: "device_ru",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Manufacturer",
      dataIndex: "manufacturer",
      key: "manufacturer",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Stack",
      dataIndex: "stack",
      key: "stack",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Parent",
      dataIndex: "parent",
      key: "parent",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Source",
      dataIndex: "source",
      key: "source",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Site Type",
      dataIndex: "site_type",
      key: "site_type",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Contract Number",
      dataIndex: "contract_number",
      key: "contract_number",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Contract Expiry",
      dataIndex: "contract_expiry",
      key: "contract_expiry",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      align: "center",
      ellipsis: true,
    },
    {
      title: "IMS Status",
      dataIndex: "ims_status",
      key: "ims_status",
      align: "center",
      ellipsis: true,
    },
    {
      title: "IMS Function",
      dataIndex: "ims_function",
      key: "ims_function",
      align: "center",
      ellipsis: true,
    },
    {
      title: "VULN Fix Plan Status",
      dataIndex: "vuln_fix_plan_status",
      key: "vuln_fix_plan_status",
      align: "center",
      ellipsis: true,
    },
    {
      title: "VULN OPS Severity",
      dataIndex: "vuln_ops_severity",
      key: "vuln_ops_severity",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Integrated with AAA",
      dataIndex: "integrated_with_aaa",
      key: "integrated_with_aaa",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Integrated with PAAM",
      dataIndex: "integrated_with_paam",
      key: "integrated_with_paam",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Approved MBSS",
      dataIndex: "approved_mbss",
      key: "approved_mbss",
      align: "center",
      ellipsis: true,
    },
    {
      title: "MBSS Integration Check",
      dataIndex: "mbss_implemented",
      key: "mbss_implemented",
      align: "center",
      ellipsis: true,
    },
    {
      title: "MBSS Integration Check",
      dataIndex: "mbss_integration_check",
      key: "mbss_integration_check",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Integrated with Siem",
      dataIndex: "integrated_with_siem",
      key: "integrated_with_siem",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Threat Cases",
      dataIndex: "threat_cases",
      key: "threat_cases",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Vulnerability Scanning",
      dataIndex: "vulnerability_scanning",
      key: "vulnerability_scanning",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Vulnerability Severity",
      dataIndex: "vulnerability_severity",
      key: "vulnerability_severity",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Creation Date",
      dataIndex: "creation_date",
      key: "creation_date",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Modification Date",
      dataIndex: "modification_date",
      key: "modification_date",
      align: "center",
      ellipsis: true,
    },
    {
      title: "Created By",
      dataIndex: "created_by",
      key: "created_by",
      align: "center",
      ellipsis: true,
      hidden: user?.user_role !== roles.admin,
    },
    {
      title: "Modified By",
      dataIndex: "modified_by",
      key: "modified_by",
      align: "center",
      ellipsis: true,
      hidden: user?.user_role !== roles.admin,
    },
  ];

  const handleFilterChange = async (value, changedFilter) => {
    setUpdateDisabled(true);

    if (changedFilter === "domain") {
      setDomain(value);
      setFunction("");
      setPnCode("");
      setDeviceId("");

      const res1 = await axios.get(
        baseUrl + `/getFunctionsForBulkUpdate?domain=${value}`
      );
      setFunctions(res1.data);

      const res2 = await axios.post(baseUrl + `/getPnCodesForBulkUpdate`, {
        domain: value,
        function: functiond,
      });
      setPnCodes(res2.data);

      const res3 = await axios.post(baseUrl + `/getDeviceIdsForBulkUpdate`, {
        domain: value,
        function: functiond,
        pn_code: pnCode,
      });
      setDeviceIds(res3.data);
    } else if (changedFilter === "function") {
      setFunction(value);
      setPnCode("");
      setDeviceId("");

      const res2 = await axios.post(baseUrl + `/getPnCodesForBulkUpdate`, {
        domain,
        function: value,
      });
      setPnCodes(res2.data);

      const res3 = await axios.post(baseUrl + `/getDeviceIdsForBulkUpdate`, {
        domain,
        function: value,
        pn_code: pnCode,
      });
      setDeviceIds(res3.data);
    } else if (changedFilter === "pn_code") {
      setPnCode(value);
      setDeviceId("");

      const res3 = await axios.post(baseUrl + `/getDeviceIdsForBulkUpdate`, {
        domain,
        function: functiond,
        pn_code: value,
      });
      setDeviceIds(res3.data);
    } else {
      setDeviceId(value);
    }
  };

  return (
    <StyledCard>
      <Spin tip="Loading..." spinning={loading}>
        <StyledHeading>
          Bulk Update
          <span
            style={{
              float: "right",
              fontSize: "14px",
              fontWeight: "bold",
              color: "grey",
              paddingTop: "10px",
            }}
          >
            Selected Rows Count: {selectedRowKeys.length} &nbsp;&nbsp;&nbsp;
            Rows: {rowCount} &nbsp;&nbsp;&nbsp; Columns: {columns.length}
          </span>
        </StyledHeading>

        <Row gutter={30}>
          <Col span={6}>
            <InputWrapper>
              Domain: &nbsp;<span style={{ color: "red" }}>*</span>
              &nbsp;&nbsp;
              <Select
                value={domain}
                style={{ width: "100%" }}
                onChange={(value) => handleFilterChange(value, "domain")}
              >
                {getDomainOptions(domains)}
              </Select>
            </InputWrapper>
          </Col>
          <Col span={6}>
            <InputWrapper>
              Function:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Select
                value={functiond}
                style={{ width: "100%" }}
                onChange={(value) => handleFilterChange(value, "function")}
              >
                {getOptions(functions)}
              </Select>
            </InputWrapper>
          </Col>
          <Col span={6}>
            <InputWrapper>
              Pn Code:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Select
                value={pnCode}
                style={{ width: "100%" }}
                onChange={(value) => handleFilterChange(value, "pn_code")}
              >
                {getOptions(pnCodes)}
              </Select>
            </InputWrapper>
          </Col>
          <Col span={6}>
            <InputWrapper>
              Device Id:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <Select
                value={deviceId}
                style={{ width: "100%" }}
                onChange={(value) => handleFilterChange(value, "device_id")}
              >
                {getOptions(deviceIds)}
              </Select>
            </InputWrapper>
          </Col>
          <Col span={24} style={{ textAlign: "center" }}>
            <StyledButton color={"red"} onClick={handleCancel}>
              Clear
            </StyledButton>
            &nbsp; &nbsp;
            <StyledButton color={"green"} onClick={() => handleSubmit()}>
              Search
            </StyledButton>
          </Col>
        </Row>
        <br />
        <div>
          <Row gutter={30}>
            <Col span={6}>
              <InputWrapper>
                PAAM Integrations:
                {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
                &nbsp;&nbsp;
                <Select
                  disabled={updateDisabled}
                  value={paamIntegrations}
                  style={{ width: "100%" }}
                  onChange={(value) => {
                    setPAAMIntegrations(value);
                  }}
                >
                  <Option value="">Choose update value</Option>
                  <Option value="Yes">Yes</Option>
                  <Option value="No">No</Option>
                  <Option value="NA">NA</Option>
                </Select>
              </InputWrapper>
            </Col>
            <Col span={6}>
              <InputWrapper>
                AAA Integrations:
                {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
                &nbsp;&nbsp;
                <Select
                  disabled={updateDisabled}
                  value={aaaIntegrations}
                  style={{ width: "100%" }}
                  onChange={(value) => {
                    setAAAIntegrations(value);
                  }}
                >
                  <Option value="">Choose update value</Option>
                  <Option value="Yes">Yes</Option>
                  <Option value="No">No</Option>
                  <Option value="NA">NA</Option>
                </Select>
              </InputWrapper>
            </Col>
            <Col span={6}>
              <InputWrapper>
                MBSS Approved:
                {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
                &nbsp;&nbsp;
                <Select
                  disabled={updateDisabled}
                  value={mbssApproved}
                  style={{ width: "100%" }}
                  onChange={(value) => {
                    setMBSSApproved(value);
                  }}
                >
                  <Option value="">Choose update value</Option>
                  <Option value="Yes">Yes</Option>
                  <Option value="No">No</Option>
                  <Option value="NA">NA</Option>
                </Select>
              </InputWrapper>
            </Col>
            <Col span={6}>
              <InputWrapper>
                MBSS Compliance:
                {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
                &nbsp;&nbsp;
                <Select
                  disabled={updateDisabled}
                  value={mbssCompliance}
                  style={{ width: "100%" }}
                  onChange={(value) => {
                    setMBSSCompliance(value);
                  }}
                >
                  <Option value="">Choose update value</Option>
                  <Option value="Yes">Yes</Option>
                  <Option value="No">No</Option>
                  <Option value="NA">NA</Option>
                </Select>
              </InputWrapper>
            </Col>
          </Row>
          <div style={{ display: "flex", justifyContent: "center" }}>
            <StyledButton
              disabled={updateDisabled}
              color={"red"}
              onClick={() => {
                setSelectedRowKeys([]);
              }}
            >
              Clear All Selection
            </StyledButton>
            &nbsp; &nbsp;
            <StyledButton
              disabled={updateDisabled}
              color={"green"}
              onClick={() => handleUpdate()}
            >
              Update
            </StyledButton>
          </div>
        </div>
        {/* </form> */}
        <StyledTable
          pagination={{
            defaultPageSize: 50,
            pageSizeOptions: [50, 100, 500, 1000],
            total,
          }}
          size="small"
          scroll={{ x: 13000, y: height - 350 }}
          onChange={handleChange}
          rowSelection={rowSelection}
          columns={columns}
          dataSource={dataSource}
          rowKey="device_id"
          //   style={{ whiteSpace: "pre" }}
        />
      </Spin>
    </StyledCard>
  );
};

export default Index;

const StyledCard = styled.div`
  margin-bottom: 20px;
  background-color: white;
  border-radius: 10px;
  padding: 25px 20px 20px 20px;
  box-shadow: rgba(99, 99, 99, 0.2) 0px 2px 8px 0px;
`;

const InputWrapper = styled.div`
  font-size: 12px;
  white-space: nowrap;
  display: flex;
  justify-content: space-between;
  padding-bottom: 10px;
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
