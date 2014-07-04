/***************************************************************************
 * 
 * Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
 * 
 **************************************************************************/

/**
 * @file bn_rp_poi_association.cpp
 * @author dengweiru(dengweiru@baidu.com)
 * @date 2014-6-26 上午2:27:37
 * @code gbk
 * @brief 
 *  
 **/
#include <string>
using std::string;

//#include "bn_rp_svr_const_data.h"
//#include "bn_rp_svr_log.h"
//#include "bn_rp_svr_conf.h"

#include "google/protobuf/text_format.h"

#include "google/protobuf/stubs/common.h"
#include "sofa/pbrpc/rpc_channel.h"
#include "sofa/pbrpc/common.h"
#include "sofa/pbrpc/rpc_controller.h"

#include <sofa/pbrpc/pbrpc.h>
#include "pbrpc.pb.h"
#include "pbrpc_service.pb.h" 
 
#include <unistd.h>
 
 
//#include "bn_rp_poi_association.h"
#include <sstream>

using lbs::da::openservice::GetBNItemsRequest;
using lbs::da::openservice::GetBNItemsResponse;
using lbs::da::openservice::ItemBytes;

void getBNitemsCallback(sofa::pbrpc::RpcController* cntl,
        sofa::pbrpc::test::EchoRequest* request,
        sofa::pbrpc::test::EchoResponse* response,
        bool* callbacked)
{
    SLOG(NOTICE, "RemoteAddress=%s", cntl->RemoteAddress().c_str());
    SLOG(NOTICE, "IsRequestSent=%s", cntl->IsRequestSent() ? "true" : "false");
    if (cntl->IsRequestSent())
    {
        SLOG(NOTICE, "LocalAddress=%s", cntl->LocalAddress().c_str());
        SLOG(NOTICE, "SentBytes=%ld", cntl->SentBytes());
    }

    if (cntl->Failed()) {
        SLOG(ERROR, "request failed: %s", cntl->ErrorText().c_str());
    }
    else {
        //SLOG(NOTICE, "request succeed: %s", response->message().c_str());
    }

    delete cntl;
    delete request;
    delete response;
    *callbacked = true;
}

int main()
{
    SOFA_PBRPC_SET_LOG_LEVEL(NOTICE);

    // Define an rpc server.
    sofa::pbrpc::RpcClientOptions client_options;
    sofa::pbrpc::RpcClient rpc_client(client_options);

    // Define an rpc channel.
    sofa::pbrpc::RpcChannelOptions channel_options;
    sofa::pbrpc::RpcChannel rpc_channel(&rpc_client, "127.0.0.1:12321", channel_options);

    // Prepare parameters.
    sofa::pbrpc::RpcController* cntl = new sofa::pbrpc::RpcController();
    cntl->SetTimeout(3000);
	
	// 填充请求包
    lbs::da::openservice::RequestHeader* header = request.mutable_header();
    header->set_servicekey("key1"); // 头部固定的字符串，laplace暂时没检查
    header->set_secretkey("pass");
    header->set_subservice("sub");
	
    sofa::pbrpc::test::EchoRequest* request = new sofa::pbrpc::test::EchoRequest();
    request->set_message("Hello from qinzuoyan01");
    sofa::pbrpc::test::EchoResponse* response = new sofa::pbrpc::test::EchoResponse();
    bool callbacked = false;
    google::protobuf::Closure* done = sofa::pbrpc::NewClosure(
            &getBNitemsCallback, cntl, request, response, &callbacked);

    // Async call.
    sofa::pbrpc::test::EchoServer_Stub stub(&rpc_channel);
    stub.Echo(cntl, request, response, done);

    // Wait call done.
    while (!callbacked) {
        usleep(100000);
    }

    return EXIT_SUCCESS;
}

/* vim: set ts=4 sw=4 sts=4 tw=100 */
