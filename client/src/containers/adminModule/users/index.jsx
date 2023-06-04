import React, { useState, useEffect, useRef } from "react";
import styled from "styled-components";
import {
  Table,
  Row,
  Col,
  Input,
  Button,
  Tabs,
  Select,
  Switch,
  Form,
  Spin,
} from "antd";
import axios, { baseUrl } from "../../../utils/axios";
import { StyledButton } from "../../../components/button/main.styles";
import { StyledHeading } from "../../../components/paragraph/main.styles";
import Swal from "sweetalert2";
import XLSX from "xlsx";
import {
  PlusOutlined,
  RightSquareOutlined,
  ReloadOutlined,
  EditOutlined,
} from "@ant-design/icons";
import { StyledTable } from "../../../components/table/main.styles";
import { columnSearch } from "../../../utils";
import Modal from "./modal";

let columnFilters = {};
let excelData = [];

const Index = (props) => {
  const { Option } = Select;
  const [loading, setLoading] = useState(false);
  let [editRecord, setEditRecord] = useState(null);
  let [sortedInfo, setSortedInfo] = useState(null);
  let [filteredInfo, setFilteredInfo] = useState(null);
  const [userId, setUserId] = useState("");
  const [emailId, setEmailId] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [role, setRole] = useState(null);
  const [status, setStatus] = useState("Active");
  const [accountType, setAccountType] = useState("Local");
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const roles = ["Admin", "User", "Executive", "Engineer", "EDN-SM"];
  const teams = [
    "PERFORMANCE",
    "DEVELOPMENT",
    "EDN",
    "IGW",
    "SOC",
    "SYSTEMS",
    "FO",
    "CABLING",
    "IPT",
    "EDN-SM",
    "IT",
    "Others",
  ];
  const vendors = ["Cisco", "Mobily"];

  const [show, setShow] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [dataSource, setDataSource] = useState([]);
  // let [dataSource, setDataSource] = useState([
  //   { user_id: "sdfaf", email_address: "dfsfsd", name: "gdfgs" },
  // ]);
  let [searchValue, setSearchValue] = useState(null);
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  const [rowCount, setRowCount] = useState(0);
  const formRef = useRef(null);
  let getColumnSearchProps = columnSearch(
    searchText,
    setSearchText,
    searchedColumn,
    setSearchedColumn
  );
  let [exportLoading, setExportLoading] = useState(false);

  const { TabPane } = Tabs;

  function callback(key) {
    console.log(key);
  }

  useEffect(() => {
    getAllMembers();
    formRef.current.setFieldsValue({
      team: "PERFORMANCE",
      vendor: "Cisco",
    });
  }, []);

  const getAllMembers = () => {
    setLoading(true);
    try {
      axios
        .get(baseUrl + "/getAllUsers")
        .then((res) => {
          setLoading(false);
          setDataSource(res.data);
          setRowCount(res.data.length);
          excelData = res.data;
          console.log(res);
        })
        .catch((err) => {
          setLoading(false);
          console.log(err);
        });
    } catch (err) {
      setLoading(false);
      console.log(err);
    }
  };

  const post = async (member) => {
    setLoading(true);
    try {
      await axios
        .post(baseUrl + "/addUser", member)
        .then((res) => {
          if (res.data.code === "409") {
            openSweetAlert(res.data.response, "danger");
            console.log("hohoho");
            console.log(res.data);
          } else {
            getAllMembers();
            openSweetAlert("Member Added Successfully", "success");
            formRef.current.resetFields();
            setLoading(false);
            console.log(res.data);
          }
        })
        .catch((err) => {
          openSweetAlert("Something Went Wrong!", "danger");
          setLoading(false);
          console.log(err);
        });
    } catch (err) {
      openSweetAlert("Something Went Wrong!", "danger");
      setLoading(false);
      console.log(err);
    }
  };

  const handleSubmit = async (values) => {
    let member = { ...values, status, account_type: accountType };
    await post(member);
    console.log(member);
  };

  const openSweetAlert = (title, type) => {
    Swal.fire({
      title,
      type,
    });
  };

  const onActiveChange = (checked) => {
    setStatus(checked ? "Active" : "Inactive");
  };

  const onUserChange = (checked) => {
    setAccountType(checked ? "Local" : "LDAP");
    setShow(!show);
  };

  const handleChange = (pagination, filters, sorter, extra) => {
    setRowCount(extra.currentDataSource.length);
    setFilteredInfo(filters);
    setSortedInfo(sorter);
  };

  const edit = (record) => {
    setEditRecord(record);
    setShowModal(true);
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

  const opensweetalertdanger = () => {
    Swal.fire({
      title: "NO Device Data Found!",
      // text: "OOPS",
      type: "warning",
    });
  };

  const handleDelete = () => {
    if (selectedRowKeys.length > 0) {
      axios
        .post(baseUrl + "/deleteUsers", {
          user_ids: selectedRowKeys,
        })
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getAllUsers")
              .then((response) => {
                console.log(response.data);
                setDataSource(response.data);
                excelData = response.data;
                setRowCount(excelData.length);
                setLoading(false);
              })
              .catch((error) => {
                console.log(error);
                setLoading(false);
              })
          );
          return Promise.all(promises);
        })
        .catch((err) => {
          console.log(err);
          setLoading(false);
        });
    } else {
      opensweetalertdanger("No device is selected to delete.");
    }
  };

  const columns = [
    {
      title: "",
      key: "edit",
      width: "35px",

      render: (text, record) => (
        <a>
          <EditOutlined
            onClick={() => {
              edit(record);
            }}
          />
        </a>
      ),
    },
    {
      title: "User Id",
      dataIndex: "user_id",
      key: "user_id",
      ...getColumnSearchProps(
        "user_id",
        "User Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Email Address",
      dataIndex: "email_address",
      key: "email_address",
      ...getColumnSearchProps(
        "email_address",
        "Email Address",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Name",
      dataIndex: "name",
      key: "name",
      ...getColumnSearchProps(
        "name",
        "Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    // {
    //   title: "Password",
    //   dataIndex: "password",
    //   key: "password",
    //   ...getColumnSearchProps(
    //     "password",
    //     "Password",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   ellipsis: true,
    // },
    {
      title: "Role",
      dataIndex: "role",
      key: "role",
      ...getColumnSearchProps(
        "role",
        "Role",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "account_type",
      key: "account_type",
      ...getColumnSearchProps(
        "account_type",
        "Account Type",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      ...getColumnSearchProps(
        "status",
        "Status",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Team",
      dataIndex: "team",
      key: "team",
      ...getColumnSearchProps(
        "team",
        "Team",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Vendor",
      dataIndex: "vendor",
      key: "vendor",
      ...getColumnSearchProps(
        "vendor",
        "Vendor",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "last_login",
      key: "last_login",
      ...getColumnSearchProps(
        "last_login",
        "Last Login",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Creation Date",
      dataIndex: "creation_date",
      key: "creation_date",
      // ...getColumnSearchProps("creation_date"),
      ...getColumnSearchProps(
        "creation_date",
        "Creation Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.creation_date.length - b.creation_date.length,
      // sortOrder: sortedInfo.columnKey === "creation_date" && sortedInfo.order,
      ellipsis: true,
    },
    // {
    //   title: "Modification Date",
    //   dataIndex: "modification_date",
    //   key: "modification_date",
    //   // ...getColumnSearchProps("modification_date"),
    //   ...getColumnSearchProps(
    //     "modification_date",
    //     "Modification Date",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   // sorter: (a, b) => a.modification_date.length - b.modification_date.length,
    //   // sortOrder:
    //   //   sortedInfo.columnKey === "modification_date" && sortedInfo.order,
    //   ellipsis: true,
    // },
  ];

  const jsonToExcel = (seedData) => {
    let wb = XLSX.utils.book_new();
    let binarySeedData = XLSX.utils.json_to_sheet(seedData);
    XLSX.utils.book_append_sheet(wb, binarySeedData, "users");
    XLSX.writeFile(wb, "users.xlsx");
    setExportLoading(false);
  };

  const exportSeed = async () => {
    setExportLoading(true);
    jsonToExcel(excelData);
    setExportLoading(false);
  };

  return (
    <StyledTabs defaultActiveKey="1" onChange={callback}>
      <TabPane tab="Add Member" key="1" style={{ border: "none" }}>
        <StyledCard style={{ marginBottom: "20px", paddingBottom: "0px" }}>
          <Form
            style={{
              paddingTop: "35px",
              borderRadius: "15px",
            }}
            autoComplete="off"
            onFinish={async (values) => {
              await handleSubmit(values);
            }}
            onFinishFailed={(error) => {
              console.log({ error });
            }}
            ref={formRef}
          >
            <Row style={{ padding: "5px" }}>
              <Col xs={24} xl={24}>
                <Form.Item
                  name="user_id"
                  label="User Id"
                  rules={[
                    {
                      required: true,
                      message: "Please enter your User Id",
                    },
                  ]}
                  hasFeedback
                >
                  <Input placeholder="Type your User Id" value={userId} block />
                </Form.Item>
              </Col>
            </Row>
            <Row style={{ padding: "5px" }}>
              <Col xs={24} xl={24}>
                <Form.Item
                  name="email_address"
                  label="Email Address"
                  rules={[
                    {
                      required: true,
                      message: "Please enter your Email Address",
                    },
                  ]}
                  hasFeedback
                >
                  <Input
                    type="email"
                    placeholder="Type your Email Address"
                    block
                  />
                </Form.Item>
              </Col>
            </Row>
            <div>
              {show ? (
                <Row style={{ padding: "5px" }} id="pasField">
                  <Col xs={24} xl={24}>
                    <Form.Item
                      name="password"
                      label="Password"
                      rules={[
                        {
                          required: true,
                          message: "Please enter your Password",
                        },
                      ]}
                      hasFeedback
                    >
                      <Input
                        type="password"
                        placeholder="Type your Password"
                        block
                      />
                    </Form.Item>
                  </Col>
                </Row>
              ) : null}
            </div>
            <Row style={{ padding: "5px" }}>
              <Col xs={24} xl={24}>
                <Form.Item
                  name="name"
                  label="Name"
                  rules={[
                    {
                      required: true,
                      message: "Please enter your Name",
                    },
                  ]}
                  hasFeedback
                >
                  <Input placeholder="Type your Name" block required={true} />
                </Form.Item>
              </Col>
            </Row>
            <Row style={{ padding: "5px" }}>
              <Col xs={24} xl={24}>
                <Form.Item
                  name="role"
                  label="Role"
                  rules={[
                    {
                      required: true,
                      message: "Please Assign Role",
                    },
                  ]}
                  hasFeedback
                >
                  <Select placeholder="Assign Role" style={{ width: "100%" }}>
                    {roles.map((role, index) => {
                      return (
                        <Select.Option key={index} value={role}>
                          {role}
                        </Select.Option>
                      );
                    })}
                  </Select>
                </Form.Item>
              </Col>
            </Row>
            <Row style={{ padding: "5px" }} justify="space-between">
              <Col span={11}>
                <Form.Item
                  name="team"
                  label="Team"
                  rules={[
                    {
                      required: true,
                      message: "Please Assign Team",
                    },
                  ]}
                  hasFeedback
                >
                  <Select placeholder="Assign Team" style={{ width: "100%" }}>
                    {teams.map((team, index) => {
                      return (
                        <Select.Option key={index} value={team}>
                          {team}
                        </Select.Option>
                      );
                    })}
                  </Select>
                </Form.Item>
              </Col>
              <Col span={11}>
                <Form.Item
                  name="vendor"
                  label="Vendor"
                  rules={[
                    {
                      required: true,
                      message: "Please Assign Vendor",
                    },
                  ]}
                  hasFeedback
                >
                  <Select placeholder="Assign Vendor" style={{ width: "100%" }}>
                    {vendors.map((vendor, index) => {
                      return (
                        <Select.Option key={index} value={vendor}>
                          {vendor}
                        </Select.Option>
                      );
                    })}
                  </Select>
                </Form.Item>
              </Col>
            </Row>
            <div style={{ textAlign: "center" }}>
              <Form.Item>
                <span style={{ marginRight: "10px", textAlign: "right" }}>
                  Active
                </span>
                <Switch defaultChecked onChange={onActiveChange} />
                &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;
                <span style={{ marginRight: "10px" }}>Local User</span>
                <Switch defaultChecked onChange={onUserChange} />
              </Form.Item>
            </div>
            <div style={{ textAlign: "center" }}>
              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  style={{
                    backgroundColor: "green",
                    borderRadius: "5px",
                    fontWeight: "500",
                    width: "15%",
                  }}
                >
                  Add Member
                </Button>
              </Form.Item>
            </div>
          </Form>
        </StyledCard>
      </TabPane>
      <TabPane tab="Show Members" key="2">
        {showModal && (
          <Modal
            isModalVisible={showModal}
            setIsModalVisible={setShowModal}
            dataSource={dataSource}
            setDataSource={setDataSource}
            editRecord={editRecord}
          />
        )}

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            padding: "0 0 10px 0",
          }}
        >
          <StyledButton onClick={handleDelete} color={"#bb0a1e"}>
            <RightSquareOutlined /> &nbsp; Delete
          </StyledButton>
          <div
            style={{
              display: "flex",
            }}
          >
            <span
              style={{
                // float: "right",
                fontSize: "14px",
                fontWeight: "bold",
                color: "grey",
                // paddingTop: "10px",
                paddingRight: "15px",
              }}
            >
              Rows: {rowCount} &nbsp;&nbsp;&nbsp; Columns: {columns.length - 1}
            </span>
            <Spin spinning={exportLoading}>
              <StyledButton color={"#3bbdc2"} onClick={exportSeed}>
                <RightSquareOutlined /> &nbsp; Export
              </StyledButton>
            </Spin>
          </div>
        </div>

        <Spin tip="Loading..." spinning={loading}>
          <StyledTable
            pagination={{
              defaultPageSize: 50,
              pageSizeOptions: [50, 100, 500, 1000],
            }}
            scroll={{ x: 2200, y: 350 }}
            rowSelection={rowSelection}
            columns={columns}
            dataSource={dataSource}
            onChange={handleChange}
            rowKey="user_id"
          />
        </Spin>
      </TabPane>
    </StyledTabs>
  );

  // return (
  //   <>
  //     <StyledTabs defaultActiveKey="1" onChange={callback}>
  //       <TabPane tab="Add Member" key="1" style={{ border: "none" }}>
  //         <StyledCard style={{ marginBottom: "20px", paddingBottom: "0px" }}>
  //           <form onSubmit={handleSubmit}>
  //             <Row gutter={30} justify="center">
  //               <Col span={24} style={{ marginTop: "35px" }}>
  //                 <InputWrapper>
  //                   User ID: &nbsp;<span style={{ color: "red" }}>*</span>
  //                   &nbsp;&nbsp;
  //                   <StyledInput
  //                     style={{ height: "2rem" }}
  //                     value={userId}
  //                     onChange={(e) => setUserId(e.target.value)}
  //                     required
  //                   />
  //                 </InputWrapper>
  //                 <InputWrapper>
  //                   Email ID: &nbsp;<span style={{ color: "red" }}>*</span>
  //                   &nbsp;&nbsp;
  //                   <StyledInput
  //                     style={{ height: "2rem" }}
  //                     type="email"
  //                     value={emailId}
  //                     onChange={(e) => setEmailId(e.target.value)}
  //                     required
  //                   />
  //                 </InputWrapper>
  //                 {localUser ? (
  //                   <InputWrapper>
  //                     Password: &nbsp;<span style={{ color: "red" }}>*</span>
  //                     &nbsp;&nbsp;
  //                     <StyledInput
  //                       style={{ height: "2rem" }}
  //                       type="password"
  //                       value={password}
  //                       onChange={(e) => setPassword(e.target.value)}
  //                       required={localUser}
  //                     />
  //                   </InputWrapper>
  //                 ) : null}
  //                 <InputWrapper>
  //                   Name: &nbsp;<span style={{ color: "red" }}>*</span>
  //                   &nbsp;&nbsp;
  //                   <StyledInput
  //                     style={{ height: "2rem" }}
  //                     value={name}
  //                     onChange={(e) => setName(e.target.value)}
  //                     required
  //                   />
  //                 </InputWrapper>
  //                 <InputWrapper>
  //                   Role: &nbsp;<span style={{ color: "red" }}>*</span>
  //                   &nbsp;&nbsp;
  //                   <Select
  //                     value={role ? role : "User"}
  //                     style={{ width: "100%" }}
  //                     onChange={(value) => {
  //                       setRole(value);
  //                     }}
  //                   >
  //                     <Option value="Administrator">Administrator</Option>
  //                     <Option value="Executive">Executive</Option>
  //                     <Option value="Engineer">Engineer</Option>
  //                     <Option value="User">User</Option>
  //                   </Select>
  //                 </InputWrapper>
  //               </Col>
  //               <Col style={{ padding: "10px 0 10px 0" }}>
  //                 Active &nbsp;&nbsp;&nbsp;
  //                 <Switch checked={active} onChange={onActiveChange} />
  //                 &nbsp;&nbsp; &nbsp; &nbsp; &nbsp; Local User
  //                 &nbsp;&nbsp;&nbsp;
  //                 <Switch checked={localUser} onChange={onUserChange} />
  //               </Col>
  //               <Col span={24} style={{ textAlign: "center" }}>
  //                 <StyledSubmitButton
  //                   color={"green"}
  //                   type="submit"
  //                   value="Add Member"
  //                   style={{ marginTop: "10px" }}
  //                 />
  //               </Col>
  //             </Row>
  //           </form>
  //           <br />
  //         </StyledCard>
  //       </TabPane>
  //       <TabPane tab="Show Members" key="2">
  //         {showModal && (
  //           <Modal
  //             isModalVisible={showModal}
  //             setIsModalVisible={setShowModal}
  //             dataSource={dataSource}
  //             setDataSource={setDataSource}
  //             editRecord={editRecord}
  //           />
  //         )}
  //         <Spin tip="Loading..." spinning={loading}>
  //           <StyledTable
  //             pagination={{
  //               defaultPageSize: 50,
  //               pageSizeOptions: [50, 100, 500, 1000],
  //             }}
  //             scroll={{ x: 1500, y: 350 }}
  //             columns={columns}
  //             dataSource={dataSource}
  //             onChange={handleChange}
  //           />
  //         </Spin>
  //       </TabPane>
  //     </StyledTabs>
  //   </>
  // );
};

const StyledTabs = styled(Tabs)`
  margin-top: -20px;
  .ant-tabs-content-holder {
    border: none;
    border-left: none !important;
    padding: 3px;
  }
`;

const StyledCard = styled.div`
  height: 100%;
  background-color: white;
  border-radius: 10px;
  padding: 0px 20px 5px 20px;
  box-shadow: rgba(99, 99, 99, 0.2) 0px 2px 8px 0px;
`;

const StyledInput = styled(Input)`
  height: 1.9rem;
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

export default Index;
