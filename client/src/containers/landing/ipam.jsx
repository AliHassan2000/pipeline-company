import React, { useEffect, useState } from "react";
import { Route } from "react-router-dom";
import { WalletOutlined } from "@ant-design/icons";
import ARP from "../ipamModule/ARP";
import { StyledMenuItem, StyledMenu } from "../landing/styles/main.styles";

export const IPAMMenu = ({ user, roles, history, location }) => {
  return (
    <>
      <StyledMenu
        user={user?.user_role}
        defaultSelectedKeys={["/"]}
        selectedKeys={[`/${location.pathname.split("/")[1]}`]}
        mode="inline"
        inlineCollapsed={false}
      >
        <>
          {!(user?.user_role === roles.executive) ? (
            <>
              <StyledMenuItem
                key="/arp"
                icon={<WalletOutlined />}
                onClick={() => history.push("/arp")}
              >
                ARP
              </StyledMenuItem>
            </>
          ) : null}
        </>
      </StyledMenu>
    </>
  );
};

export const IPAMRoutes = ({ user, roles }) => {
  return (
    <>
      {user?.user_role !== roles.ednSM ? (
        <>
          {user?.user_role !== roles.executive ? (
            <>
              <Route exact path="/arp" component={ARP} />
            </>
          ) : null}
        </>
      ) : null}
    </>
  );
};
