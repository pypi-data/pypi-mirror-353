# Copyright 2021-2025 ONDEWO GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from google.protobuf.empty_pb2 import Empty

from ondewo.nlu import operations_pb2
from ondewo.nlu.agent_pb2 import (
    AddUserToProjectRequest,
    Agent,
    BuildCacheRequest,
    CreateAgentRequest,
    DeleteAgentRequest,
    DeleteResourcesRequest,
    ExportAgentRequest,
    ExportBenchmarkAgentRequest,
    ExportResourcesRequest,
    ExportResourcesResponse,
    FullTextSearchRequest,
    FullTextSearchResponseEntity,
    FullTextSearchResponseEntitySynonym,
    FullTextSearchResponseEntityType,
    FullTextSearchResponseIntent,
    FullTextSearchResponseIntentContextIn,
    FullTextSearchResponseIntentContextOut,
    FullTextSearchResponseIntentParameters,
    FullTextSearchResponseIntentResponse,
    FullTextSearchResponseIntentTags,
    FullTextSearchResponseIntentUsersays,
    GetAgentRequest,
    GetAgentStatisticsRequest,
    GetAgentStatisticsResponse,
    GetModelStatusesRequest,
    GetModelStatusesResponse,
    GetPlatformInfoResponse,
    GetPlatformMappingRequest,
    GetSessionsStatisticsRequest,
    GetSessionsStatisticsResponse,
    ImportAgentRequest,
    ListAgentsOfUserResponse,
    ListAgentsRequest,
    ListAgentsResponse,
    ListProjectPermissionsRequest,
    ListProjectPermissionsResponse,
    ListUsersInProjectRequest,
    ListUsersInProjectResponse,
    OptimizeRankingMatchRequest,
    PlatformMapping,
    ReindexAgentRequest,
    RemoveUserFromProjectRequest,
    RestoreAgentRequest,
    SetAgentStatusRequest,
    SetResourcesRequest,
    TrainAgentRequest,
    UpdateAgentRequest,
)
from ondewo.nlu.agent_pb2_grpc import AgentsStub
from ondewo.nlu.core.services_interface import ServicesInterface


class Agents(ServicesInterface):
    """
    Exposes the agent-related endpoints of ONDEWO NLU services in a user-friendly way.

    See agent.proto.
    """

    @property
    def stub(self) -> AgentsStub:
        stub: AgentsStub = AgentsStub(channel=self.grpc_channel)
        return stub

    def create_agent(self, request: CreateAgentRequest) -> Agent:
        response: Agent = self.stub.CreateAgent(request, metadata=self.metadata)
        return response

    def update_agent(self, request: UpdateAgentRequest) -> Agent:
        response: Agent = self.stub.UpdateAgent(request, metadata=self.metadata)
        return response

    def get_agent(self, request: GetAgentRequest) -> Agent:
        response: Agent = self.stub.GetAgent(request, metadata=self.metadata)
        return response

    def delete_agent(self, request: DeleteAgentRequest) -> Empty:
        response: Empty = self.stub.DeleteAgent(request, metadata=self.metadata)
        return response

    def delete_all_agents(self) -> Empty:
        response: Empty = self.stub.DeleteAllAgents(Empty(), metadata=self.metadata)
        return response

    def list_agents(self, request: ListAgentsRequest) -> ListAgentsResponse:
        response: ListAgentsResponse = self.stub.ListAgents(request, metadata=self.metadata)
        return response

    def list_agents_of_user(self, request: ListAgentsRequest) -> ListAgentsOfUserResponse:
        response: ListAgentsOfUserResponse = self.stub.ListAgentsOfUser(request, metadata=self.metadata)
        return response

    def list_all_agents(self, request: ListAgentsRequest) -> ListAgentsResponse:
        response: ListAgentsResponse = self.stub.ListAllAgents(request, metadata=self.metadata)
        return response

    def add_user_to_project(self, request: AddUserToProjectRequest) -> Empty:
        response: Empty = self.stub.AddUserToProject(request, metadata=self.metadata)
        return response

    def remove_user_from_project(self, request: RemoveUserFromProjectRequest) -> Empty:
        response: Empty = self.stub.RemoveUserFromProject(request, metadata=self.metadata)
        return response

    def list_users_in_project(self, request: ListUsersInProjectRequest) -> ListUsersInProjectResponse:
        response: ListUsersInProjectResponse = self.stub.ListUsersInProject(request, metadata=self.metadata)
        return response

    def get_platform_info(self) -> GetPlatformInfoResponse:
        response: GetPlatformInfoResponse = self.stub.GetPlatformInfo(Empty(), metadata=self.metadata)
        return response

    def list_project_permissions(
        self,
        request: ListProjectPermissionsRequest
    ) -> ListProjectPermissionsResponse:
        response: ListProjectPermissionsResponse = \
            self.stub.ListProjectPermissions(request, metadata=self.metadata)
        return response

    def train_agent(self, request: TrainAgentRequest) -> operations_pb2.Operation:
        response: operations_pb2.Operation = self.stub.TrainAgent(request, metadata=self.metadata)
        return response

    def build_cache(self, request: BuildCacheRequest) -> operations_pb2.Operation:
        response: operations_pb2.Operation = self.stub.BuildCache(request, metadata=self.metadata)
        return response

    def export_agent(self, request: ExportAgentRequest) -> operations_pb2.Operation:
        response: operations_pb2.Operation = self.stub.ExportAgent(request, metadata=self.metadata)
        return response

    def export_benchmark_agent(self, request: ExportBenchmarkAgentRequest) -> operations_pb2.Operation:
        response: operations_pb2.Operation = self.stub.ExportBenchmarkAgent(request, metadata=self.metadata)
        return response

    def import_agent(self, request: ImportAgentRequest) -> operations_pb2.Operation:
        response: operations_pb2.Operation = self.stub.ImportAgent(request, metadata=self.metadata)
        return response

    def optimize_ranking_match(self, request: OptimizeRankingMatchRequest) -> operations_pb2.Operation:
        response: operations_pb2.Operation = self.stub.OptimizeRankingMatch(request, metadata=self.metadata)
        return response

    def restore_agent(self, request: RestoreAgentRequest) -> operations_pb2.Operation:
        response: operations_pb2.Operation = self.stub.RestoreAgent(request, metadata=self.metadata)
        return response

    def get_agent_statistics(self, request: GetAgentStatisticsRequest) -> GetAgentStatisticsResponse:
        response: GetAgentStatisticsResponse = self.stub.GetAgentStatistics(request, metadata=self.metadata)
        return response

    def get_sessions_statistics(self, request: GetSessionsStatisticsRequest) -> GetSessionsStatisticsResponse:
        response: GetSessionsStatisticsResponse = self.stub.GetSessionsStatistics(request, metadata=self.metadata)
        return response

    def set_agent_status(self, request: SetAgentStatusRequest) -> Agent:
        response: Agent = self.stub.SetAgentStatus(request, metadata=self.metadata)
        return response

    def set_resources(self, request: SetResourcesRequest) -> Empty:
        response: Empty = self.stub.SetResources(request, metadata=self.metadata)
        return response

    def delete_resources(self, request: DeleteResourcesRequest) -> Empty:
        response: Empty = self.stub.DeleteResources(request, metadata=self.metadata)
        return response

    def export_resources(self, request: ExportResourcesRequest) -> ExportResourcesResponse:
        response: ExportResourcesResponse = self.stub.ExportResources(request, metadata=self.metadata)
        return response

    def get_model_statuses(self, request: GetModelStatusesRequest) -> GetModelStatusesResponse:
        response: GetModelStatusesResponse = self.stub.GetModelStatuses(request, metadata=self.metadata)
        return response

    def get_platform_mapping(self, request: GetPlatformMappingRequest) -> PlatformMapping:
        response: PlatformMapping = self.stub.GetPlatformMapping(request, metadata=self.metadata)
        return response

    def set_platform_mapping(self, request: PlatformMapping) -> PlatformMapping:
        response: PlatformMapping = self.stub.SetPlatformMapping(request, metadata=self.metadata)
        return response

    def get_full_text_search_entity(self, request: FullTextSearchRequest) -> FullTextSearchResponseEntity:
        response: FullTextSearchResponseEntity = self.stub.GetFullTextSearchEntity(request, metadata=self.metadata)
        return response

    def get_full_text_search_entity_type(self, request: FullTextSearchRequest) -> FullTextSearchResponseEntityType:
        response: FullTextSearchResponseEntityType = \
            self.stub.GetFullTextSearchEntityType(request, metadata=self.metadata)
        return response

    def get_full_text_search_entity_synonym(
        self,
        request: FullTextSearchRequest,
    ) -> FullTextSearchResponseEntitySynonym:
        response: FullTextSearchResponseEntitySynonym = \
            self.stub.GetFullTextSearchEntitySynonym(request, metadata=self.metadata)
        return response

    def get_full_text_search_intent(
        self,
        request: FullTextSearchRequest,
    ) -> FullTextSearchResponseIntent:
        response: FullTextSearchResponseIntent = \
            self.stub.GetFullTextSearchIntent(request, metadata=self.metadata)
        return response

    def get_full_text_search_intent_context_in(
        self,
        request: FullTextSearchRequest,
    ) -> FullTextSearchResponseIntentContextIn:
        response: FullTextSearchResponseIntentContextIn = \
            self.stub.GetFullTextSearchIntentContextIn(request, metadata=self.metadata)
        return response

    def get_full_text_search_intent_context_out(
        self,
        request: FullTextSearchRequest,
    ) -> FullTextSearchResponseIntentContextOut:
        response: FullTextSearchResponseIntentContextOut = \
            self.stub.GetFullTextSearchIntentContextOut(request, metadata=self.metadata)
        return response

    def get_full_text_search_intent_usersays(
        self,
        request: FullTextSearchRequest,
    ) -> FullTextSearchResponseIntentUsersays:
        response: FullTextSearchResponseIntentUsersays = \
            self.stub.GetFullTextSearchIntentUsersays(request, metadata=self.metadata)
        return response

    def get_full_text_search_intent_tags(
        self,
        request: FullTextSearchRequest,
    ) -> FullTextSearchResponseIntentTags:
        response: FullTextSearchResponseIntentTags = \
            self.stub.GetFullTextSearchIntentTags(request, metadata=self.metadata)
        return response

    def get_full_text_search_intent_response(
        self,
        request: FullTextSearchRequest,
    ) -> FullTextSearchResponseIntentResponse:
        response: FullTextSearchResponseIntentResponse = \
            self.stub.GetFullTextSearchIntentResponse(request, metadata=self.metadata)
        return response

    def get_full_text_search_intent_parameters(
        self,
        request: FullTextSearchRequest,
    ) -> FullTextSearchResponseIntentParameters:
        response: FullTextSearchResponseIntentParameters = \
            self.stub.GetFullTextSearchIntentParameters(request, metadata=self.metadata)
        return response

    def reindex_agent(self, request: ReindexAgentRequest) -> operations_pb2.Operation:
        response: operations_pb2.Operation = self.stub.ReindexAgent(request, metadata=self.metadata)
        return response
