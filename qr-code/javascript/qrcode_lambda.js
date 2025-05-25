const AWS = require('aws-sdk');
const QRCode = require('qrcode');
const { v4: uuidv4 } = require('uuid');

/**
 * Lambda function that generates a QR code from a URL, uploads it to S3,
 * and stores the URL and image location in DynamoDB.
 *
 * This function:
 * 1. Takes a URL input from the event
 * 2. Generates a QR code image
 * 3. Uploads the image to S3
 * 4. Stores the URL and image location in DynamoDB
 * 5. Returns the S3 URL of the generated image
 *
 * The Lambda function requires these permissions:
 * s3:PutObject (for storing the QR code image)
 * dynamodb:PutItem (for storing URL data)
 *
 * Example test event:
 * {
 *   "url": "https://aws.amazon.com",
 *   "bucket": "your-s3-bucket-name",
 *   "tableName": "qrcode-urls",
 *   "filename": "my-qrcode.png"  // Optional
 * }
 */
exports.handler = async (event, context) => {
  // Get parameters from the event
  const url = event.url;
  const bucket = event.bucket;
  const tableName = event.tableName;
  let filename = event.filename;

  // Validate required parameters
  if (!url) {
    return {
      statusCode: 400,
      body: JSON.stringify({
        message: 'URL is required',
      }),
    };
  }

  if (!bucket) {
    return {
      statusCode: 400,
      body: JSON.stringify({
        message: 'S3 bucket name is required',
      }),
    };
  }

  if (!tableName) {
    return {
      statusCode: 400,
      body: JSON.stringify({
        message: 'DynamoDB table name is required',
      }),
    };
  }

  // Generate a filename if not provided
  if (!filename) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    filename = `qrcode-${timestamp}.png`;
  }

  try {
    // Initialize AWS clients
    const s3 = new AWS.S3();
    const dynamodb = new AWS.DynamoDB.DocumentClient();

    // Generate QR code as PNG buffer
    const qrBuffer = await QRCode.toBuffer(url, {
      errorCorrectionLevel: 'L',
      type: 'png',
      margin: 4,
      scale: 10,
    });

    // Upload to S3
    const s3Key = `qrcodes/${filename}`;
    await s3
      .putObject({
        Bucket: bucket,
        Key: s3Key,
        Body: qrBuffer,
        ContentType: 'image/png',
      })
      .promise();

    // Generate a pre-signed URL (valid for 1 hour)
    const presignedUrl = s3.getSignedUrl('getObject', {
      Bucket: bucket,
      Key: s3Key,
      Expires: 3600,
    });

    // Store URL data in DynamoDB
    const itemId = uuidv4();
    const timestamp = new Date().toISOString();
    const s3Uri = `s3://${bucket}/${s3Key}`;

    await dynamodb
      .put({
        TableName: tableName,
        Item: {
          id: itemId,
          url: url,
          s3Uri: s3Uri,
          createdAt: timestamp,
        },
      })
      .promise();

    // Return success response
    return {
      statusCode: 200,
      body: JSON.stringify({
        message: 'QR code generated successfully',
        id: itemId,
        s3Uri: s3Uri,
        presignedUrl: presignedUrl,
        url: url,
        createdAt: timestamp,
      }),
    };
  } catch (error) {
    console.error('Error generating QR code:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({
        message: 'Error generating QR code',
        error: error.message,
      }),
    };
  }
};
