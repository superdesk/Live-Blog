Feature: Embed


Scenario: Check what newly added post was published
    When GET /LiveDesk/Blog/1/Post/Published?cId.since=8
    Then status is 200
    And json contains
      | total | lastCId |
      | 1     | 9       |

    When GET /my/LiveDesk/Blog/1/Post/$last_id
    Then status is 200
    And json contains
      """
      {"Id": "$last_id", "IsPublished": "True"}
      """


Scenario: Edit post
    When PUT /my/LiveDesk/Blog/1/Post/$last_id
      """
      {"Content": "test changed"}
      """
    Then status is 200

    When GET /LiveDesk/Blog/1/Post/Published?cId.since=9
    Then status is 200
    And json contains
      """
      {"total": "1", "lastCId": "10"}
      """

    When GET /my/LiveDesk/Blog/1/Post/$last_id
    Then status is 200
    And json contains
      """
      {"Id": "$last_id", "IsPublished": "True", "Content": "test changed"}
      """


Scenario: Unpublish post
    When POST /my/LiveDesk/Blog/1/Post/$last_id/Unpublish
    Then status is 201

    When GET /LiveDesk/Blog/1/Post/Published?cId.since=9
    Then status is 200
    And json contains
      """
      {"total": "1", "lastCId": "10"}
      """

    When GET /my/LiveDesk/Blog/1/Post/$last_id with headers
      """
      {"X-Filter": "Id,IsPublished"}
      """
    Then status is 200
    And json contains
      """
      {"Id": "$last_id", "IsPublished": "False"}
      """


Scenario: Delete post
    When DELETE /my/Data/Post/$last_id
    Then status is 204

    When GET /LiveDesk/Blog/1/Post/Published?cId.since=9
    Then status is 200
    And json contains
      """
      {"total": "1", "lastCId": "10"}
      """

    When GET /my/LiveDesk/Blog/1/Post/$last_id
    Then status is 200
    But json contains
      """
      DeletedOn
      """


Scenario: Blog settings
    When PUT /my/LiveDesk/Blog/1
      """
      {"EmbedConfig": "{\"theme\":\"tageswoche-multi\",\"FrontendServer\":\"//localhost:8080\",\"MediaImage\":\"//localhost:8080/content/media_archive/audio/000/2.23.jpeg\",\"VerificationToggle\":\"on\",\"MediaToggle\":\"true\",\"MediaUrl\":\"//www.sourcefabric.org\",\"UserComments\":\"true\"}"}
      """
    Then status is 200
    When GET /LiveDesk/Blog/1
    Then status is 200
    And EmbedConfig json contains
    """
      "{\"theme\":\"tageswoche-multi\",\"FrontendServer\":\"//localhost:8080\",\"MediaImage\":\"//localhost:8080/content/media_archive/audio/000/2.23.jpeg\",\"VerificationToggle\":\"on\",\"MediaToggle\":\"true\",\"MediaUrl\":\"//www.sourcefabric.org\",\"UserComments\":\"true\"}"
    """


Scenario: Pagination for posts
    Given 20 fixtures

    When GET /LiveDesk/Blog/1/Post/Published?limit=15
    Then status is 200
    And PostList json length is 15

    When GET /LiveDesk/Blog/1/Post/Published?offset=15&limit=15
    Then status is 200
    And PostList json length is 12
