package com.zinnia.zenius.repository;
import com.zinnia.zenius.model.GeneratedTestCase;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface GeneratedTestCaseRepository extends MongoRepository<GeneratedTestCase, String> {
    @Query(value = "{ 'source': ?0, 'sourceId': ?1 }", sort = "{ '_id' : -1 }")
    List<GeneratedTestCase> findBySourceAndJiraOrConfluenceId(String source, String sourceId);

    @Query(value = "{ 'source': ?0, 'hash': ?1 }", sort = "{ '_id' : -1 }")
    List<GeneratedTestCase> findBySourceAndHash(String source, String hash);

}
