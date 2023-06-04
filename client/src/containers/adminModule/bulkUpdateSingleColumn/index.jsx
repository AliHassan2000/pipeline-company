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
// import SearchForm from "./modals/macLegacySearch";
import XLSX from "xlsx";
import axios, { baseUrl } from "../../../utils/axios";
import Search from "../../../components/search";
import { StyledTable } from "../../../components/table/main.styles";
import { StyledButton } from "../../../components/button/main.styles";
import { StyledHeading } from "../../../components/paragraph/main.styles";
import { StyledImportFileInput } from "../../../components/input/main.styles";
import {
  PlusOutlined,
  RightSquareOutlined,
  ReloadOutlined,
  EditOutlined,
  DownOutlined,
} from "@ant-design/icons";
import Swal from "sweetalert2";
import { Link, useHistory } from "react-router-dom";
// import { SEED_API } from "../../../GlobalVar";
// import ShowSeedDevice from "../../../seed/ShowSeedDevice";
import { columnSearch } from "../../../utils";
import useWindowDimensions from "../../../hooks/useWindowDimensions";
import { roles } from "../../../utils/constants.js";
import Modal from "./modal";

let columnFilters = {};
let excelData = [];
const Index = (props) => {
  const { height, width } = useWindowDimensions();
  const { Option } = Select;
  const [dates, setDates] = useState([]);
  const [user, setUser] = useState();
  let [loading, setLoading] = useState(false);
  let [exportLoading, setExportLoading] = useState(false);
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
  const ref = useRef();
  const [isModalVisible, setIsModalVisible] = useState(false);
  let [columnsArray, setColumnsArray] = useState([]);

  useEffect(() => {
    const serviceCalls = async () => {
      // setLoading(true);
      try {
        await axios.get(baseUrl + "/getAllDeviceStaticColumns").then((res) => {
          setColumnsArray(res.data);
        });
        // setLoading(false);
      } catch (err) {
        console.log(err.response);
        // setLoading(false)
      }
    };
    serviceCalls();
  }, []);

  //   useEffect(() => {
  //     const serviceCalls = async () => {
  //       setLoading(true);
  //       setUser(JSON.parse(localStorage.getItem("user")));
  //       try {
  //         await axios
  //           .get(baseUrl + "/getAllEdnMacLegacyDates")
  //           .then((response) => {
  //             setDates(response.data);
  //             setFetchDate(response.data?.length > 0 ? response.data[0] : null);
  //             console.log(response);
  //           });
  //         setLoading(false);
  //       } catch (err) {
  //         console.log(err.response);
  //         setLoading(false);
  //       }
  //     };
  //     serviceCalls();
  //   }, []);

  let [deviceId, setDeviceId] = useState("");
  let [ipAddress, setIpAddress] = useState("");
  let [functiond, setFunction] = useState("");

  const getOptions = (values = []) => {
    let options = [];
    values.map((value) => {
      options.push(<Option value={value}>{value}</Option>);
    });
    return options;
  };

  const getDataBySearchFilters = async (filters, pageSize, currentPage) => {
    setLoading(true);
    await axios
      .post(
        baseUrl +
          `/getDevicesBySearchFilters?limit=${pageSize}&offset=${
            pageSize * (currentPage - 1)
          }`,
        filters
      )
      .then((response) => {
        setRowCount(response.data.data.length);
        setDataSource(response.data.data);
        setTotal(response.data.total);
        setLoading(false);
      })
      .catch((error) => {
        console.log(error);
        setLoading(false);
      });
  };

  const handleSubmit = (pageSize, currentPage) => {
    const filters = {
      device_id: deviceId,
      ip_address: ipAddress,
      function: functiond,
    };

    getDataBySearchFilters(filters, pageSize, currentPage);
  };

  const checkProperties = (obj) => {
    for (let key in obj) {
      if (obj[key] !== null && obj[key] != "") return true;
    }
    return false;
  };

  const handleCancel = async () => {
    setDeviceId("");
    setIpAddress("");
    setFunction("");
  };

  //   const handleSelectChange = (value) => {
  //     setFetchDate(value);
  //   };

  const exportSeed = async () => {
    // setExportLoading(true);
    // jsonToExcel(dataSource, "ednmaclegacySearched.xlsx");
    // setExportLoading(false);
    const filters = {
      //   device_a_name: deviceAName,
      //   device_a_ip: deviceAIp,
      //   device_b_ip: deviceBIp,
      //   device_b_mac: deviceBMac,
      //   device_a_vlan: deviceAVlan,
      //   device_b_system_name: deviceBSystemName,
      //   server_name: serverName,
      //   app_name: appName,
      //   service_vendor: serviceVendor,
      //   fetch_date: fetchDate,
    };

    await axios
      .post(baseUrl + "/exportEdnMacLegacySearched", filters)
      .then((response) => {
        jsonToExcel(response.data, "ednmaclegacySearched.xlsx");
        console.log(response);
        setExportLoading(false);
      })
      .catch((error) => {
        setExportLoading(false);
        console.log(error);
      });
  };

  const jsonToExcel = (seedData, fileName) => {
    let wb = XLSX.utils.book_new();
    let binarySeedData = XLSX.utils.json_to_sheet(seedData);
    XLSX.utils.book_append_sheet(wb, binarySeedData, "seeds");
    XLSX.writeFile(wb, fileName);
    setExportLoading(false);
  };

  const onSelectChange = (selectedRowKeys) => {
    console.log("selectedRowKeys changed: ", selectedRowKeys);
    setSelectedRowKeys(selectedRowKeys);
  };

  const rowSelection = {
    selectedRowKeys,
    onChange: onSelectChange,
    selection: Table.SELECTION_ALL,
  };

  const handleChange = (pagination, filters, sorter, extra) => {
    console.log("Various parameters", pagination, filters, sorter, extra);
    handleSubmit(pagination.pageSize, pagination.current);
    setPageSize(pagination.pageSize);
    setCurrentPage(pagination.current);
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

  const handleUpdate = () => {
    setIsModalVisible(true);
  };

  return (
    <StyledCard>
      {isModalVisible ? (
        <Modal
          isModalVisible={isModalVisible}
          setIsModalVisible={setIsModalVisible}
          columnsArray={columnsArray}
          deviceId={deviceId}
          ipAddress={ipAddress}
          functiond={functiond}
        />
      ) : null}
      <Spin tip="Loading..." spinning={loading}>
        <StyledHeading>
          Bulk Update Devices Single Column
          <span
            style={{
              float: "right",
              fontSize: "14px",
              fontWeight: "bold",
              color: "grey",
              paddingTop: "10px",
            }}
          >
            Rows: {total} &nbsp;&nbsp;&nbsp; Columns: {columns.length}
          </span>
        </StyledHeading>

        <div
          style={{
            // border: "1px solid black",
            marginTop: "0px",
            display: "flex",
            justifyContent: "space-between",
            padding: "0 0 10px 0",
          }}
        >
          <div></div>
          <div style={{ display: "flex" }}>
            <StyledButton
              color={"#3bbdc2"}
              onClick={handleUpdate}
              style={{ width: "100%" }}
            >
              <RightSquareOutlined /> Update
            </StyledButton>
          </div>
        </div>

        {/* <form onSubmit={handleSubmit}> */}
        <Row gutter={30}>
          <Col span={8}>
            <InputWrapper>
              Device Id:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={deviceId}
                onChange={(e) => setDeviceId(e.target.value)}
                // required
              />
            </InputWrapper>
          </Col>
          <Col span={8}>
            <InputWrapper>
              Ip Address:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={ipAddress}
                onChange={(e) => setIpAddress(e.target.value)}
                // required
              />
            </InputWrapper>
          </Col>
          <Col span={8}>
            <InputWrapper>
              Function:
              {/* &nbsp;<span style={{ color: "red" }}>*</span> */}
              &nbsp;&nbsp;
              <StyledInput
                value={functiond}
                onChange={(e) => setFunction(e.target.value)}
                // required
              />
            </InputWrapper>
          </Col>
          <Col span={24} style={{ textAlign: "center" }}>
            <StyledButton2 color={"red"} onClick={handleCancel}>
              Clear
            </StyledButton2>
            &nbsp; &nbsp;
            <StyledButton2
              color={"green"}
              onClick={() => handleSubmit(pageSize, currentPage)}
            >
              Search
            </StyledButton2>
          </Col>
        </Row>
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
          // rowSelection={rowSelection}
          columns={columns}
          dataSource={dataSource}
          //   rowKey="edn_mac_legacy_id"
          //   style={{ whiteSpace: "pre" }}
        />
      </Spin>
    </StyledCard>
  );
};

export default Index;

const StyledCard = styled.div`
  /* margin-top: -10px; */
  margin-bottom: 20px;
  /* height: 100%; */
  /* text-align: center; */
  background-color: white;
  border-radius: 10px;
  padding: 25px 20px 20px 20px;
  box-shadow: rgba(99, 99, 99, 0.2) 0px 2px 8px 0px;
`;

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

const StyledButton2 = styled(Button)`
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
